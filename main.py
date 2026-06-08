import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from Token import BOT_TOKEN
from handlers import user
from database.models import async_main

TOKEN = BOT_TOKEN



async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход")


