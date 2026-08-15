import asyncio

from app.bot import bot, dp
from app.database.db import init_db

from app.handlers import start
from app.handlers import trading
from app.handlers import orders


async def main():
    print("🤖 Запуск P2P бота...")

    await init_db()

    print("🗄️ База данных подключена")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
