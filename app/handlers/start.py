from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot import dp
from app.database.repositories import get_or_create_user
from app.keyboards import main_menu


@dp.message(Command("start"))
async def start_handler(message: Message):

    user, is_new = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    if is_new:
        text = (
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Вы успешно зарегистрированы."
        )
    else:
        text = (
            "👋 <b>С возвращением!</b>\n\n"
            "Главное меню:"
        )

    await message.answer(
        text,
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
