from aiogram import Dispatcher, Bot
import asyncio
import os
from dotenv import load_dotenv
import logging
from crud import init_db
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)


async def main():
    try:
        logging.info('Bot start')
        await init_db()
        dp.include_router(router)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    asyncio.run(main())
