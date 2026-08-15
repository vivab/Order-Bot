import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


TOKEN = "8943979043:AAFvMbx9sEki6SxNhmqzC3ImjuB1gEKPkws"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не указан")


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "P2P-маркет пока находится в разработке."
    )


async def main():
    bot = Bot(token=TOKEN)

    try:
        print("🤖 Бот запущен")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
