import asyncio

from app.bot import bot, dp

# Подключаем handlers
from app.handlers import start
from app.handlers import trading
from app.handlers import orders


async def main():
    print("🤖 P2P бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
