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
    "Карта": 1.0,
    "Абонемент": 1.0,
    "Бесплатно": 0.0,
}

TIME_OPTIONS = [
    "13:00",
    "14:00",
    "15:00",
    "16:00",
]
