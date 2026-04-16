from datetime import datetime
from typing import Any
from config import TEACHER_SHARE

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
        f"Итого учеников: {students_count}",
        f"Базовая сумма: {sum(s['base_amount'] for s in students):.2f}",
        f"Общая сумма: {total_amount:.2f}",
    ])

    return "\n".join(lines)
