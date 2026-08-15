from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.bot import dp
from app.keyboards import main_menu, back_main


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Это P2P-маркет с системой гарантов "
        "для безопасных сделок.\n\n"
        "Выберите раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "menu:main")
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "menu:profile")
async def profile_handler(callback: CallbackQuery):
    user = callback.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "не указан"
    )

    await callback.message.edit_text(
        "👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Username: {username}\n\n"
        "📅 В боте с: будет добавлено после подключения БД\n"
        "👍 Положительных отзывов: 0\n"
        "👎 Отрицательных отзывов: 0\n"
        "💰 Оборот за 30 дней: 0\n"
        "💰 Оборот за всё время: 0",
        reply_markup=back_main(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "menu:guarantors")
async def guarantors_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡️ <b>Актуальные гаранты</b>\n\n"
        "Список гарантов пока пуст.",
        reply_markup=back_main(),
        parse_mode="HTML"
    )

    await callback.answer()
