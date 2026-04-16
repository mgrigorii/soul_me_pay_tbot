from aiogram.fsm.state import State, StatesGroup


class LessonForm(StatesGroup):
    choosing_lesson_date_mode = State()
    waiting_for_manual_lesson_date = State()
    choosing_lesson_time = State()
    waiting_for_manual_lesson_time = State()
    waiting_for_students_count = State()
    waiting_for_student_name = State()
    waiting_for_payment_method = State()
    waiting_for_confirmation = State()
    waiting_for_report_action = State()
