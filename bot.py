import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import router


async def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в .env")

    await asyncio.sleep(3)  # даём старому инстансу умереть

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
