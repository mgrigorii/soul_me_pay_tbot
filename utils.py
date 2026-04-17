import asyncio
from datetime import datetime
from typing import Any

import requests

from config import (
    TEACHER_SHARE,
    GOOGLE_APPS_SCRIPT_ENABLED,
    GOOGLE_APPS_SCRIPT_URL,
    GOOGLE_APPS_SCRIPT_SECRET,
    BASE_AMOUNT_DEFAULT,
    LESSON_PRICE_BY_TELEGRAM_ID,
)


def is_allowed_user(user_id: int, allowed_user_ids: set[int]) -> bool:
    if not allowed_user_ids:
        return True
    return user_id in allowed_user_ids


def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_time(time_text: str) -> bool:
    try:
        datetime.strptime(time_text, "%H:%M")
        return True
    except ValueError:
        return False


def validate_students_count(text: str) -> bool:
    if not text.isdigit():
        return False
    value = int(text)
    return 1 <= value <= 50


def calculate_final_amount(base_amount: float, coefficient: float) -> float:
    return round(base_amount * coefficient, 2)


def get_base_amount_for_user(telegram_id: int | None) -> float:
    if telegram_id is None:
        return BASE_AMOUNT_DEFAULT
    return float(LESSON_PRICE_BY_TELEGRAM_ID.get(telegram_id, BASE_AMOUNT_DEFAULT))


def _build_rows_for_google_sheet(lesson_data: dict[str, Any], telegram_id: int) -> list[dict[str, Any]]:
    lesson_id = lesson_data.get("lesson_id", "")
    lesson_date = lesson_data["lesson_date"]
    lesson_time = lesson_data["lesson_time"]
    students = lesson_data["students"]

    total_amount = round(sum(student["final_amount"] for student in students), 2)
    teacher_amount = round(total_amount * TEACHER_SHARE, 2)

    rows = []
    for idx, student in enumerate(students, start=1):
        rows.append(
            {
                "lesson_id": lesson_id,
                "telegram_id": telegram_id,
                "lesson_date": lesson_date,
                "lesson_time": lesson_time,
                "students_count": len(students),
                "student_index": idx,
                "student_name": student["name"],
                "payment_method": student["payment_method"],
                "base_amount": student["base_amount"],
                "coefficient": student["coefficient"],
                "final_amount": student["final_amount"],
                "lesson_total_amount": total_amount,
                "teacher_amount": teacher_amount,
            }
        )
    return rows


async def save_lesson_to_google_sheet(lesson_data: dict[str, Any], telegram_id: int) -> None:
    if not GOOGLE_APPS_SCRIPT_ENABLED or not GOOGLE_APPS_SCRIPT_URL:
        return

    rows = _build_rows_for_google_sheet(lesson_data, telegram_id)
    payload = {
        "secret": GOOGLE_APPS_SCRIPT_SECRET,
        "rows": rows,
    }

    def _send() -> None:
        response = requests.post(GOOGLE_APPS_SCRIPT_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("error", "Unknown Google Apps Script error"))

    await asyncio.to_thread(_send)


def build_lesson_report(lesson_data: dict[str, Any]) -> str:
    lesson_date = lesson_data["lesson_date"]
    lesson_time = lesson_data["lesson_time"]
    students = lesson_data["students"]

    total_amount = round(sum(student["final_amount"] for student in students), 2)
    teacher_amount = round(total_amount * TEACHER_SHARE, 2)

    lines = [
        "Отчет по уроку",
        "",
        f"Дата: {lesson_date}",
        f"Время: {lesson_time}",
        "",
    ]

    for idx, student in enumerate(students, start=1):
        name = student["name"]
        payment_method = student["payment_method"]
        final_amount = student["final_amount"]
        lines.append(f"{idx}. {name} — {payment_method} — {final_amount:.2f}")

    lines.extend([
        "",
        f"Всего учеников: {len(students)}",
        f"Общий итог: {total_amount:.2f}",
        f"К оплате учителю (60% от финальной суммы): {teacher_amount:.2f}",
    ])

    return "\n".join(lines)


def build_confirmation_text(lesson_data: dict[str, Any]) -> str:
    lesson_date = lesson_data["lesson_date"]
    lesson_time = lesson_data["lesson_time"]
    students_count = lesson_data["students_count"]
    students = lesson_data["students"]

    total_amount = round(sum(student["final_amount"] for student in students), 2)
    teacher_amount = round(total_amount * TEACHER_SHARE, 2)
    share_percent = int(TEACHER_SHARE * 100)

    lines = [
        "Проверьте данные",
        "",
        f"День урока: {lesson_date}",
        f"Время урока: {lesson_time}",
        f"Количество учеников: {students_count}",
        "",
    ]

    for idx, student in enumerate(students, start=1):
        lines.append(
            f"{idx}. {student['name']} — {student['payment_method']} — {student['final_amount']:.2f}"
        )

    lines.extend([
        "",
        f"Общий итог: {total_amount:.2f}",
        f"К оплате учителю ({share_percent}%): {teacher_amount:.2f}",
    ])

    return "\n".join(lines)
