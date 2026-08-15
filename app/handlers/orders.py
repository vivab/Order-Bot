from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot import dp
from app.states import CreateOrderStates
from app.keyboards import (
    order_type_keyboard,
    fiat_keyboard,
    coin_keyboard,
    conditions_keyboard,
    confirmation_keyboard,
)


# Временное хранилище.
# Позже полностью заменим PostgreSQL.
orders = {}


@dp.callback_query(F.data == "trading:create")
async def create_order_start(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(CreateOrderStates.order_type)

    await callback.message.edit_text(
        "➕ <b>Создание сделки</b>\n\n"
        "Что вы хотите сделать?",
        reply_markup=order_type_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    CreateOrderStates.order_type,
    F.data.startswith("order_type:")
)
async def choose_order_type(
    callback: CallbackQuery,
    state: FSMContext
):
    order_type = callback.data.split(":")[1]

    await state.update_data(order_type=order_type)
    await state.set_state(CreateOrderStates.fiat)

    await callback.message.edit_text(
        "💱 Выберите валюту оплаты:",
        reply_markup=fiat_keyboard()
    )

    await callback.answer()


@dp.callback_query(
    CreateOrderStates.fiat,
    F.data.startswith("fiat:")
)
async def choose_fiat(
    callback: CallbackQuery,
    state: FSMContext
):
    fiat = callback.data.split(":")[1]

    await state.update_data(fiat=fiat)
    await state.set_state(CreateOrderStates.coin)

    await callback.message.edit_text(
        "🪙 Выберите криптовалюту:",
        reply_markup=coin_keyboard()
    )

    await callback.answer()


@dp.callback_query(
    CreateOrderStates.coin,
    F.data.startswith("coin:")
)
async def choose_coin(
    callback: CallbackQuery,
    state: FSMContext
):
    coin = callback.data.split(":")[1]

    await state.update_data(coin=coin)
    await state.set_state(CreateOrderStates.amount)

    data = await state.get_data()

    if data["order_type"] == "sell":
        text = (
            f"🪙 <b>Количество {coin}</b>\n\n"
            f"Введите количество {coin}, которое хотите продать.\n\n"
            "Например: <code>10</code>"
        )
    else:
        text = (
            f"💰 <b>Сумма в {data['fiat']}</b>\n\n"
            "Введите сумму или диапазон.\n\n"
            "Например:\n"
            "<code>5000</code>\n"
            "или\n"
            "<code>1000-10000</code>"
        )

    await callback.message.edit_text(
        text,
        parse_mode="HTML"
    )

    await callback.answer()


@dp.message(CreateOrderStates.amount)
async def enter_amount(
    message: Message,
    state: FSMContext
):
    amount = message.text.strip()

    if not amount:
        await message.answer("❌ Введите сумму.")
        return

    await state.update_data(amount=amount)
    await state.set_state(CreateOrderStates.rate)

    data = await state.get_data()

    await message.answer(
        f"💵 <b>Курс</b>\n\n"
        f"Введите курс {data['coin']} в {data['fiat']}.\n\n"
        "Например: <code>95</code>",
        parse_mode="HTML"
    )


@dp.message(CreateOrderStates.rate)
async def enter_rate(
    message: Message,
    state: FSMContext
):
    rate = message.text.strip()

    if not rate:
        await message.answer("❌ Введите курс.")
        return

    await state.update_data(rate=rate)
    await state.set_state(CreateOrderStates.conditions)

    await message.answer(
        "📝 <b>Условия сделки</b>\n\n"
        "Напишите условия продавца/покупателя.\n"
        "Это необязательно.",
        reply_markup=conditions_keyboard(),
        parse_mode="HTML"
    )


@dp.message(CreateOrderStates.conditions)
async def enter_conditions(
    message: Message,
    state: FSMContext
):
    conditions = message.text.strip()

    await state.update_data(conditions=conditions)
    await show_confirmation(message, state)


@dp.callback_query(
    CreateOrderStates.conditions,
    F.data == "conditions:none"
)
async def no_conditions(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.update_data(conditions="")
    await show_confirmation(callback.message, state)
    await callback.answer()


async def show_confirmation(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    order_type = (
        "🔴 Продажа"
        if data["order_type"] == "sell"
        else "🟢 Покупка"
    )

    conditions = data["conditions"] or "Не указаны"

    text = (
        "📋 <b>Проверьте параметры</b>\n\n"
        f"Тип: {order_type}\n"
        f"Валюта: {data['fiat']}\n"
        f"Монета: {data['coin']}\n"
        f"Сумма: {data['amount']}\n"
        f"Курс: {data['rate']} {data['fiat']}\n"
        f"Условия: {conditions}\n\n"
        "Всё верно?"
    )

    await state.set_state(CreateOrderStates.confirmation)

    await message.answer(
        text,
        reply_markup=confirmation_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(
    CreateOrderStates.confirmation,
    F.data == "order:publish"
)
async def publish_order(
    callback: CallbackQuery,
    state: FSMContext
):
    user_id = callback.from_user.id
    data = await state.get_data()

    # Максимум 1 активный ордер.
    if user_id in orders:
        await callback.answer(
            "❌ У вас уже есть активный ордер.",
            show_alert=True
        )
        return

    orders[user_id] = {
        "user_id": user_id,
        **data,
        "active": True,
    }

    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Сделка опубликована!</b>\n\n"
        "Ваш ордер добавлен в список актуальных.",
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    CreateOrderStates.confirmation,
    F.data == "order:edit"
)
async def edit_order(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(CreateOrderStates.order_type)

    await callback.message.edit_text(
        "✏️ Выберите тип сделки заново:",
        reply_markup=order_type_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "order:cancel")
async def cancel_order(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.clear()

    await callback.message.edit_text(
        "❌ <b>Создание сделки отменено.</b>",
        parse_mode="HTML"
    )

    await callback.answer()
