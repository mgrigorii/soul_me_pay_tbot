from datetime import datetime
import uuid

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import (
    ALLOWED_USER_IDS,
    PAYMENT_COEFFICIENTS,
    TIME_OPTIONS,
    REPORT_CHAT_ID,
)
from states import LessonForm
from keyboards import (
    date_mode_keyboard,
    time_keyboard,
    students_count_keyboard,
    payment_keyboard,
    confirmation_keyboard,
    report_keyboard,
)
from utils import (
    is_allowed_user,
    validate_date,
    validate_time,
    validate_students_count,
    calculate_final_amount,
    build_confirmation_text,
    build_lesson_report,
    get_base_amount_for_user,
    save_lesson_to_google_sheet,
)

router = Router()


async def start_new_lesson_flow(message: Message, state: FSMContext) -> None:
    await state.clear()

    lesson_id = str(uuid.uuid4())

    await state.update_data(
        lesson_id=lesson_id,
        lesson_date=None,
        lesson_time=None,
        students_count=0,
        current_student_index=0,
        current_student_name=None,
        students=[],
    )

    await state.set_state(LessonForm.choosing_lesson_date_mode)
    await message.answer(
        "Выберите день урока",
        reply_markup=date_mode_keyboard(),
    )


def access_denied(user_id: int) -> bool:
    return not is_allowed_user(user_id, ALLOWED_USER_IDS)


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext) -> None:
    if access_denied(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return

    await message.answer("Привет. Я помогу занести данные по уроку.")
    await start_new_lesson_flow(message, state)


@router.message(F.text == "/new")
async def cmd_new(message: Message, state: FSMContext) -> None:
    if access_denied(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return

    await start_new_lesson_flow(message, state)


@router.callback_query(LessonForm.choosing_lesson_date_mode, F.data == "date_mode:today")
async def process_today_date(callback: CallbackQuery, state: FSMContext) -> None:
    lesson_date = datetime.now().strftime("%d.%m.%Y")
    await state.update_data(lesson_date=lesson_date)
    await state.set_state(LessonForm.choosing_lesson_time)

    await callback.answer()
    await callback.message.answer(
        f"Дата урока: {lesson_date}\n\nВыберите время урока",
        reply_markup=time_keyboard(),
    )


@router.callback_query(LessonForm.choosing_lesson_date_mode, F.data == "date_mode:manual")
async def process_manual_date_request(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(LessonForm.waiting_for_manual_lesson_date)
    await callback.answer()
    await callback.message.answer(
        "Введите день урока в формате ДД.ММ.ГГГГ\nНапример: 16.04.2026"
    )


@router.message(LessonForm.waiting_for_manual_lesson_date)
async def process_manual_date(message: Message, state: FSMContext) -> None:
    date_text = message.text.strip()

    if not validate_date(date_text):
        await message.answer(
            "Неверный формат даты.\nВведите дату в формате ДД.ММ.ГГГГ\nНапример: 16.04.2026"
        )
        return

    await state.update_data(lesson_date=date_text)
    await state.set_state(LessonForm.choosing_lesson_time)

    await message.answer(
        f"Дата урока: {date_text}\n\nВыберите время урока",
        reply_markup=time_keyboard(),
    )


@router.callback_query(LessonForm.choosing_lesson_time, F.data.startswith("time:"))
async def process_time_choice(callback: CallbackQuery, state: FSMContext) -> None:
    time_value = callback.data.split(":", 1)[1]

    if time_value == "manual":
        await state.set_state(LessonForm.waiting_for_manual_lesson_time)
        await callback.answer()
        await callback.message.answer(
            "Введите время урока в формате ЧЧ:ММ\nНапример: 15:00"
        )
        return

    if time_value not in TIME_OPTIONS:
        await callback.answer("Неизвестное время", show_alert=True)
        return

    await state.update_data(lesson_time=time_value)
    await state.set_state(LessonForm.waiting_for_students_count)

    await callback.answer()
    await callback.message.answer(
        "Сколько учеников было на уроке?",
        reply_markup=students_count_keyboard(),
    )


@router.message(LessonForm.waiting_for_manual_lesson_time)
async def process_manual_time(message: Message, state: FSMContext) -> None:
    time_text = message.text.strip()

    if not validate_time(time_text):
        await message.answer(
            "Неверный формат времени.\nВведите время в формате ЧЧ:ММ\nНапример: 15:00"
        )
        return

    await state.update_data(lesson_time=time_text)
    await state.set_state(LessonForm.waiting_for_students_count)

    await message.answer(
        "Сколько учеников было на уроке?",
        reply_markup=students_count_keyboard(),
    )


@router.callback_query(LessonForm.waiting_for_students_count, F.data.startswith("students_count:"))
async def process_students_count_callback(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]

    if value == "manual":
        await state.set_state(LessonForm.waiting_for_students_count)
        await callback.answer()
        await callback.message.answer("Введите количество учеников числом. Например: 2")
        return

    if not validate_students_count(value):
        await callback.answer("Некорректное количество", show_alert=True)
        return

    await callback.answer()
    await _save_students_count_and_ask_name(callback.message, state, int(value))


@router.message(LessonForm.waiting_for_students_count)
async def process_students_count(message: Message, state: FSMContext) -> None:
    text = message.text.strip()

    if not validate_students_count(text):
        await message.answer(
            "Пожалуйста, введите количество учеников числом от 1 до 50.\nНапример: 2"
        )
        return

    await _save_students_count_and_ask_name(message, state, int(text))


async def _save_students_count_and_ask_name(message: Message, state: FSMContext, students_count: int) -> None:
    await state.update_data(
        students_count=students_count,
        current_student_index=0,
        students=[],
    )
    await state.set_state(LessonForm.waiting_for_student_name)
    await message.answer("Введите имя ученика 1")


@router.message(LessonForm.waiting_for_student_name)
async def process_student_name(message: Message, state: FSMContext) -> None:
    student_name = message.text.strip()

    if not student_name:
        await message.answer("Имя не должно быть пустым. Введите имя ученика.")
        return

    await state.update_data(current_student_name=student_name)
    await state.set_state(LessonForm.waiting_for_payment_method)

    await message.answer(
        f"Выберите способ оплаты для {student_name}",
        reply_markup=payment_keyboard(),
    )


@router.callback_query(LessonForm.waiting_for_payment_method, F.data.startswith("payment:"))
async def process_payment_method(callback: CallbackQuery, state: FSMContext) -> None:
    payment_method = callback.data.split(":", 1)[1]

    data = await state.get_data()
    student_name = data["current_student_name"]
    current_student_index = data["current_student_index"]
    students_count = data["students_count"]
    students = data["students"]

    telegram_id = callback.from_user.id if callback.from_user else None
    base_amount = get_base_amount_for_user(telegram_id)
    coefficient = PAYMENT_COEFFICIENTS.get(payment_method, 1.0)
    final_amount = calculate_final_amount(base_amount, coefficient)

    students.append(
        {
            "name": student_name,
            "payment_method": payment_method,
            "base_amount": base_amount,
            "coefficient": coefficient,
            "final_amount": final_amount,
        }
    )

    current_student_index += 1

    await state.update_data(
        students=students,
        current_student_index=current_student_index,
        current_student_name=None,
    )

    await callback.answer("Способ оплаты сохранен.")

    if current_student_index < students_count:
        await state.set_state(LessonForm.waiting_for_student_name)
        await callback.message.answer(f"Введите имя ученика {current_student_index + 1}")
        return

    lesson_data = await state.get_data()
    confirmation_text = build_confirmation_text(lesson_data)

    await state.set_state(LessonForm.waiting_for_confirmation)
    await callback.message.answer(
        confirmation_text,
        reply_markup=confirmation_keyboard(),
    )


@router.callback_query(LessonForm.waiting_for_confirmation, F.data == "confirm:no")
async def process_confirmation_no(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Ввод отменен.")
    await callback.message.answer("Ввод отменен. Чтобы начать заново, отправьте /new")


@router.callback_query(LessonForm.waiting_for_confirmation, F.data == "confirm:yes")
async def process_confirmation_yes(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    save_error = None
    try:
        await save_lesson_to_google_sheet(data, callback.from_user.id)
    except Exception as exc:
        save_error = str(exc)

    report_text = build_lesson_report(data)

    await state.update_data(report_text=report_text)
    await state.set_state(LessonForm.waiting_for_report_action)

    await callback.answer("Данные сохранены.")
    if save_error:
        await callback.message.answer(
            "Данные по уроку сохранены в боте, но запись в Google Sheet не удалась.\n"
            f"Ошибка: {save_error}"
        )
    else:
        await callback.message.answer("Данные сохранены.\n\nВот готовый отчет:")

    await callback.message.answer(report_text, reply_markup=report_keyboard())


@router.callback_query(LessonForm.waiting_for_report_action, F.data == "report:send")
async def process_send_report(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    report_text = data.get("report_text", "")

    if not report_text:
        await callback.answer("Отчет не найден.", show_alert=True)
        return

    if REPORT_CHAT_ID is None:
        await callback.answer("REPORT_CHAT_ID еще не настроен.", show_alert=True)
        return

    await callback.bot.send_message(chat_id=REPORT_CHAT_ID, text=report_text)

    await callback.answer("Отчет отправлен.")
    await callback.message.answer("Отчет успешно отправлен.")


@router.callback_query(LessonForm.waiting_for_report_action, F.data == "report:new_lesson")
async def process_new_lesson_from_report(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_new_lesson_flow(callback.message, state)
