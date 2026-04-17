import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

allowed_raw = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = {
    int(user_id.strip())
    for user_id in allowed_raw.split(",")
    if user_id.strip().isdigit()
}

REPORT_CHAT_ID_RAW = os.getenv("REPORT_CHAT_ID", "").strip()
REPORT_CHAT_ID = int(REPORT_CHAT_ID_RAW) if REPORT_CHAT_ID_RAW.lstrip("-").isdigit() else None

BASE_AMOUNT_DEFAULT = 150.0
TEACHER_SHARE = 0.60

# Можно переопределять цену урока для конкретного telegram_id.
# Если id не найден в словаре, будет использован BASE_AMOUNT_DEFAULT.
LESSON_PRICE_BY_TELEGRAM_ID = {
    # 123456789: 180.0,
}

PAYMENT_METHODS = [
    "Наличные",
    "PIX",
    "Карта",
    "Абонемент",
    "Бесплатно",
]

PAYMENT_COEFFICIENTS = {
    "Наличные": 1.0,
    "PIX": 1.0,
    "Карта": 0.957,
    "Абонемент": 1.0,
    "Бесплатно": 0.0,
}

TIME_OPTIONS = [
    "14:00",
    "15:30",
    "17:00",
    "18:30",
]

STUDENTS_COUNT_OPTIONS = ["1", "2", "3", "4", "5"]

GOOGLE_APPS_SCRIPT_ENABLED = os.getenv("GOOGLE_APPS_SCRIPT_ENABLED", "false").lower() == "true"
GOOGLE_APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL", "").strip()
GOOGLE_APPS_SCRIPT_SECRET = os.getenv("GOOGLE_APPS_SCRIPT_SECRET", "").strip()
