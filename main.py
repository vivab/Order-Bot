import asyncio

from app.bot import bot, dp

from app.handlers import start
from app.handlers import trading
from app.handlers import orders


async def main():
    print("🤖 P2P бот запущен")

    cleanup_task = asyncio.create_task(
        orders.order_cleanup_loop()
    )

    try:
        await dp.start_polling(bot)

    finally:
        cleanup_task.cancel()

        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
