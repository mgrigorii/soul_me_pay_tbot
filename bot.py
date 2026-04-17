import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError, TelegramConflictError

from config import BOT_TOKEN
from handlers import router


async def run_bot() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в .env")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook cleared. Starting polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main() -> None:
    restart_delay = 5

    while True:
        try:
            logging.info("Starting bot...")
            await run_bot()

        except TelegramUnauthorizedError:
            logging.exception("Bot token is invalid. Check BOT_TOKEN in .env")
            break

        except TelegramConflictError:
            logging.exception("Another bot instance is running with the same token.")
            logging.info("Retrying in %s seconds...", restart_delay)
            await asyncio.sleep(restart_delay)

        except TelegramNetworkError:
            logging.exception("Network problem or Telegram API is unavailable.")
            logging.info("Retrying in %s seconds...", restart_delay)
            await asyncio.sleep(restart_delay)

        except Exception:
            logging.exception("Unexpected crash.")
            logging.info("Retrying in %s seconds...", restart_delay)
            await asyncio.sleep(restart_delay)

        else:
            logging.warning("Polling stopped without exception. Restarting in %s seconds...", restart_delay)
            await asyncio.sleep(restart_delay)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    asyncio.run(main())