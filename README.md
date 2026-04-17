# soul_me_pay_tbot

Telegram bot for tracking lessons and payments.

## Что обновлено
- кнопки выбора даты, времени и количества учеников теперь идут как inline-кнопки в сообщениях
- для количества учеников есть кнопки `1 2 3 4 5 Ввести`
- в данные добавлен `telegram_id`
- стоимость урока можно задавать по `telegram_id` в `config.py`
- запись в Google Sheet идет через Google Apps Script Web App

## Настройки `.env`
Пример:

```env
BOT_TOKEN=...
ALLOWED_USER_IDS=123456789
REPORT_CHAT_ID=-1001234567890

GOOGLE_APPS_SCRIPT_ENABLED=true
GOOGLE_APPS_SCRIPT_URL=https://script.google.com/macros/s/.../exec
GOOGLE_APPS_SCRIPT_SECRET=MY_SUPER_SECRET_TOKEN_123
```

## Цена урока по telegram_id
В `config.py`:

```python
LESSON_PRICE_BY_TELEGRAM_ID = {
    # 123456789: 180.0,
}
```
