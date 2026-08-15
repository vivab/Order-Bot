import os

from aiogram import Bot, Dispatcher


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не найден. Проверь настройки BotHost."
    )


bot = Bot(token=TOKEN)
dp = Dispatcher()
