from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TIME_OPTIONS, PAYMENT_METHODS


def date_mode_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сегодня"),
                KeyboardButton(text="Ввести дату"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def time_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t) for t in TIME_OPTIONS],
            [KeyboardButton(text="Ввести вручную")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True
    )


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
