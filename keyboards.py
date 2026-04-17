from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TIME_OPTIONS, PAYMENT_METHODS, STUDENTS_COUNT_OPTIONS


def date_mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Сегодня", callback_data="date_mode:today"),
        InlineKeyboardButton(text="Ввести дату", callback_data="date_mode:manual"),
    )
    return builder.as_markup()


def time_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for time_value in TIME_OPTIONS:
        builder.add(
            InlineKeyboardButton(text=time_value, callback_data=f"time:{time_value}")
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="Ввести вручную", callback_data="time:manual")
    )
    return builder.as_markup()


def students_count_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for count in STUDENTS_COUNT_OPTIONS:
        builder.add(
            InlineKeyboardButton(text=count, callback_data=f"students_count:{count}")
        )
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(text="Ввести", callback_data="students_count:manual")
    )
    return builder.as_markup()


def payment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for method in PAYMENT_METHODS:
        builder.add(
            InlineKeyboardButton(
                text=method,
                callback_data=f"payment:{method}"
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm:yes"),
        InlineKeyboardButton(text="Отменить", callback_data="confirm:no"),
    )
    return builder.as_markup()


def report_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Отправить отчет", callback_data="report:send")
    )
    builder.row(
        InlineKeyboardButton(text="Новый урок", callback_data="report:new_lesson")
    )
    return builder.as_markup()
