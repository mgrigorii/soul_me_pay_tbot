from datetime import datetime
import uuid

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from config import (
    ALLOWED_USER_IDS,
    BASE_AMOUNT_DEFAULT,
    PAYMENT_COEFFICIENTS,
    TIME_OPTIONS,
    REPORT_CHAT_ID,
)
from states import LessonForm
from keyboards import (
    date_mode_keyboard,
    time_keyboard,
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
)

router = Router()


async def start_new_lesson_flow(message: Message, state: FSMContext) -> None:
    await state.clear()

    lesson_id = str(uuid.uuid4())
    
    await state.update_data(
        lesson_id=lesson_id,   # 👈 ВОТ ЭТО ДОБАВИЛИ
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

    await message.answer(
        "Привет. Я помогу занести данные по уроку."
    )
    await start_new_lesson_flow(message, state)


@router.message(F.text == "/new")
async def cmd_new(message: Message, state: FSMContext) -> None:
    if access_denied(message.from_user.id):
        await message.answer("У вас нет доступа к этому боту.")
        return

    await start_new_lesson_flow(message, state)


@router.message(LessonForm.choosing_lesson_date_mode, F.text == "Сегодня")
async def process_today_date(message: Message, state: FSMContext) -> None:
    lesson_date = datetime.now().strftime("%d.%m.%Y")
    await state.update_data(lesson_date=lesson_date)
    await state.set_state(LessonForm.choosing_lesson_time)

    await message.answer(
        f"Дата урока: {lesson_date}\n\nВыберите время урока",
        reply_markup=time_keyboard(),
    )


@router.message(LessonForm.choosing_lesson_date_mode, F.text == "Ввести дату")
async def process_manual_date_request(message: Message, state: FSMContext) -> None:
    await state.set_state(LessonForm.waiting_for_manual_lesson_date)
    await message.answer(
        "Введите день урока в формате ДД.ММ.ГГГГ\nНапример: 16.04.2026",
        reply_markup=ReplyKeyboardRemove(),
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


@router.message(LessonForm.choosing_lesson_time, F.text.in_(TIME_OPTIONS))
async def process_time_choice(message: Message, state: FSMContext) -> None:
    await state.update_data(lesson_time=message.text.strip())
    await state.set_state(LessonForm.waiting_for_students_count)

    await message.answer(
        "Сколько учеников было на уроке?",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(LessonForm.choosing_lesson_time, F.text == "Ввести вручную")
async def process_manual_time_request(message: Message, state: FSMContext) -> None:
    await state.set_state(LessonForm.waiting_for_manual_lesson_time)
    await message.answer(
        "Введите время урока в формате ЧЧ:ММ\nНапример: 15:00",
        reply_markup=ReplyKeyboardRemove(),
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

    await message.answer("Сколько учеников было на уроке?")


@router.message(LessonForm.waiting_for_students_count)
async def process_students_count(message: Message, state: FSMContext) -> None:
    text = message.text.strip()

    if not validate_students_count(text):
        await message.answer(
            "Пожалуйста, введите количество учеников числом.\nНапример: 2"
        )
        return

    students_count = int(text)

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

    data = await state.get_data()
    current_student_index = data["current_student_index"]

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

    base_amount = BASE_AMOUNT_DEFAULT
    coefficient = PAYMENT_COEFFICIENTS.get(payment_method, 1.0)
    final_amount = calculate_final_amount(base_amount, coefficient)

    students.append({
        "name": student_name,
        "payment_method": payment_method,
        "base_amount": base_amount,
        "coefficient": coefficient,
        "final_amount": final_amount,
    })

    current_student_index += 1

    await state.update_data(
        students=students,
        current_student_index=current_student_index,
        current_student_name=None,
    )

    await callback.answer("Способ оплаты сохранен.")

    if current_student_index < students_count:
        await state.set_state(LessonForm.waiting_for_student_name)
        await callback.message.answer(
            f"Введите имя ученика {current_student_index + 1}"
        )
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
    await callback.message.answer(
        "Ввод отменен. Чтобы начать заново, отправьте /new"
    )


@router.callback_query(LessonForm.waiting_for_confirmation, F.data == "confirm:yes")
async def process_confirmation_yes(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    # Здесь позже можно будет добавить запись в Google Sheets
    # Например:
    # await save_lesson_to_google_sheets(data, callback.from_user)

    report_text = build_lesson_report(data)

    await state.update_data(report_text=report_text)
    await state.set_state(LessonForm.waiting_for_report_action)

    await callback.answer("Данные сохранены.")
    await callback.message.answer(
        "Данные сохранены.\n\nВот готовый отчет:",
    )
    await callback.message.answer(
        report_text,
        reply_markup=report_keyboard(),
    )


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

    await callback.bot.send_message(
        chat_id=REPORT_CHAT_ID,
        text=report_text,
    )

    await callback.answer("Отчет отправлен.")
    await callback.message.answer("Отчет успешно отправлен.")


@router.callback_query(LessonForm.waiting_for_report_action, F.data == "report:new_lesson")
async def process_new_lesson_from_report(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_new_lesson_flow(callback.message, state)
