import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


TOKEN = "8943979043:AAFvMbx9sEki6SxNhmqzC3ImjuB1gEKPkws"


dp = Dispatcher()


# =========================
# Клавиатуры
# =========================

def main_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="💱 Торговля",
        callback_data="menu:trading"
    )

    builder.button(
        text="👤 Профиль",
        callback_data="menu:profile"
    )

    builder.button(
        text="🛡️ Актуальные гаранты",
        callback_data="menu:guarantors"
    )

    builder.adjust(1)

    return builder.as_markup()


def back_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="◀️ Главное меню",
        callback_data="menu:main"
    )

    return builder.as_markup()


# =========================
# /start
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Это P2P-маркет с системой гарантов "
        "для безопасного проведения сделок.\n\n"
        "Выберите раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


# =========================
# Главное меню
# =========================

@dp.callback_query(F.data == "menu:main")
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите раздел:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# Торговля
# =========================

@dp.callback_query(F.data == "menu:trading")
async def trading_handler(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🟢 Купить",
        callback_data="trading:buy"
    )

    builder.button(
        text="🔴 Продать",
        callback_data="trading:sell"
    )

    builder.button(
        text="📋 Мои сделки",
        callback_data="trading:my"
    )

    builder.button(
        text="➕ Создать сделку",
        callback_data="trading:create"
    )

    builder.button(
        text="◀️ Назад",
        callback_data="menu:main"
    )

    builder.adjust(2, 1, 1)

    await callback.message.edit_text(
        "💱 <b>Торговля</b>\n\n"
        "Выберите действие:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# Профиль
# =========================

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
        reply_markup=back_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# Гаранты
# =========================

@dp.callback_query(F.data == "menu:guarantors")
async def guarantors_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡️ <b>Актуальные гаранты</b>\n\n"
        "Список гарантов пока пуст.\n\n"
        "Система гарантов будет подключена на следующем этапе.",
        reply_markup=back_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# Торговые кнопки — временно
# =========================

@dp.callback_query(F.data.startswith("trading:"))
async def trading_action_handler(callback: CallbackQuery):
    await callback.answer(
        "Этот раздел пока находится в разработке.",
        show_alert=True
    )


# =========================
# Запуск
# =========================

async def main():
    bot = Bot(token=TOKEN)

    try:
        print("🤖 P2P бот запущен")
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
