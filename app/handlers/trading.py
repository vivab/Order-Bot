from aiogram import F
from aiogram.types import CallbackQuery

from app.bot import dp
from app.keyboards import trading_menu


@dp.callback_query(F.data == "menu:trading")
async def trading_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "💱 <b>Торговля</b>\n\n"
        "Выберите действие:",
        reply_markup=trading_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "trading:buy")
async def buy_handler(callback: CallbackQuery):
    await callback.answer(
        "Список ордеров будет добавлен следующим этапом.",
        show_alert=True
    )


@dp.callback_query(F.data == "trading:sell")
async def sell_handler(callback: CallbackQuery):
    await callback.answer(
        "Список ордеров будет добавлен следующим этапом.",
        show_alert=True
    )


@dp.callback_query(F.data == "trading:my")
async def my_trades_handler(callback: CallbackQuery):
    from app.handlers.orders import get_user_orders_text

    text, keyboard = get_user_orders_text(
        callback.from_user.id
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await callback.answer()
