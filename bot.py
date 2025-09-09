
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from db.database import init_db
from handlers import ua
from config import BOT_TOKEN

async def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is empty. Put it into .env")
    init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(ua.router)
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
