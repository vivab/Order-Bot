import asyncio
import time
from typing import Optional

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
    my_order_keyboard,
)


# ============================================================
# ВРЕМЕННОЕ ХРАНИЛИЩЕ
# ============================================================

orders: dict[int, dict] = {}

_next_order_id = 1


def get_next_order_id() -> int:
    global _next_order_id

    order_id = _next_order_id
    _next_order_id += 1

    return order_id


# ============================================================
# Вспомогательные функции
# ============================================================

def order_is_active(order: dict) -> bool:
    if not order["active"]:
        return False

    if time.time() >= order["expires_at"]:
        order["active"] = False
        return False

    return True


def get_user_active_order(user_id: int) -> Optional[dict]:
    for order in orders.values():
        if order["user_id"] == user_id:
            if order_is_active(order):
                return order

    return None


def format_order(order: dict) -> str:
    order_type = (
        "🔴 Продажа"
        if order["order_type"] == "sell"
        else "🟢 Покупка"
    )

    conditions = order["conditions"] or "Не указаны"

    status = (
        "🟢 Активен"
        if order_is_active(order)
        else "⚪ Неактивен"
    )

    return (
        f"📋 <b>Ордер #{order['id']}</b>\n\n"
        f"Статус: {status}\n"
        f"Тип: {order_type}\n"
        f"Валюта: {order['fiat']}\n"
        f"Монета: {order['coin']}\n"
        f"Сумма: {order['amount']}\n"
        f"Курс: {order['rate']} {order['fiat']}\n"
        f"Условия: {conditions}\n"
    )


def get_user_orders_text(user_id: int):
    user_orders = [
        order
        for order in orders.values()
        if order["user_id"] == user_id
    ]

    if not user_orders:
        return (
            "📋 <b>Мои сделки</b>\n\n"
            "У вас пока нет ордеров."
        ), None

    # Берём последний ордер.
    order = sorted(
        user_orders,
        key=lambda x: x["id"],
        reverse=True
    )[0]

    return (
        "📋 <b>Мои сделки</b>\n\n"
        + format_order(order)
    ), my_order_keyboard(
        order["id"],
        order_is_active(order)
    )


# ============================================================
# СОЗДАНИЕ ОРДЕРА
# ============================================================

@dp.callback_query(F.data == "trading:create")
async def create_order_start(
    callback: CallbackQuery,
    state: FSMContext
):
    existing = get_user_active_order(
        callback.from_user.id
    )

    if existing:
        await callback.answer(
            "❌ У вас уже есть активный ордер.",
            show_alert=True
        )
        return

    await state.set_state(
        CreateOrderStates.order_type
    )

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

    await state.update_data(
        order_type=order_type
    )

    await state.set_state(
        CreateOrderStates.fiat
    )

    await callback.message.edit_text(
        "💱 <b>Выберите валюту оплаты:</b>",
        reply_markup=fiat_keyboard(),
        parse_mode="HTML"
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

    await state.update_data(
        fiat=fiat
    )

    await state.set_state(
        CreateOrderStates.coin
    )

    await callback.message.edit_text(
        "🪙 <b>Выберите криптовалюту:</b>",
        reply_markup=coin_keyboard(),
        parse_mode="HTML"
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

    await state.update_data(
        coin=coin
    )

    await state.set_state(
        CreateOrderStates.amount
    )

    data = await state.get_data()

    if data["order_type"] == "sell":
        text = (
            f"🪙 <b>Количество {coin}</b>\n\n"
            f"Введите количество {coin}, "
            "которое хотите продать.\n\n"
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
        await message.answer(
            "❌ Введите сумму."
        )
        return

    await state.update_data(
        amount=amount
    )

    await state.set_state(
        CreateOrderStates.rate
    )

    data = await state.get_data()

    await message.answer(
        f"💵 <b>Курс</b>\n\n"
        f"Введите курс {data['coin']} "
        f"в {data['fiat']}.\n\n"
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
        await message.answer(
            "❌ Введите курс."
        )
        return

    await state.update_data(
        rate=rate
    )

    await state.set_state(
        CreateOrderStates.conditions
    )

    await message.answer(
        "📝 <b>Условия сделки</b>\n\n"
        "Напишите условия.\n"
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

    await state.update_data(
        conditions=conditions
    )

    await show_confirmation(
        message,
        state
    )


@dp.callback_query(
    CreateOrderStates.conditions,
    F.data == "conditions:none"
)
async def no_conditions(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.update_data(
        conditions=""
    )

    await show_confirmation(
        callback.message,
        state
    )

    await callback.answer()


async def show_confirmation(
    message,
    state: FSMContext
):
    data = await state.get_data()

    order_type = (
        "🔴 Продажа"
        if data["order_type"] == "sell"
        else "🟢 Покупка"
    )

    conditions = (
        data["conditions"]
        if data["conditions"]
        else "Не указаны"
    )

    text = (
        "📋 <b>Проверьте параметры</b>\n\n"
        f"Тип: {order_type}\n"
        f"Валюта: {data['fiat']}\n"
        f"Монета: {data['coin']}\n"
        f"Сумма: {data['amount']}\n"
        f"Курс: {data['rate']} "
        f"{data['fiat']}\n"
        f"Условия: {conditions}\n\n"
        "Всё верно?"
    )

    await state.set_state(
        CreateOrderStates.confirmation
    )

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

    existing = get_user_active_order(user_id)

    if existing:
        await callback.answer(
            "❌ У вас уже есть активный ордер.",
            show_alert=True
        )
        return

    data = await state.get_data()

    order_id = get_next_order_id()

    orders[order_id] = {
        "id": order_id,
        "user_id": user_id,
        "order_type": data["order_type"],
        "fiat": data["fiat"],
        "coin": data["coin"],
        "amount": data["amount"],
        "rate": data["rate"],
        "conditions": data["conditions"],
        "active": True,
        "created_at": time.time(),
        "expires_at": time.time() + 3600,
    }

    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Ордер опубликован!</b>\n\n"
        f"Номер ордера: <code>#{order_id}</code>\n\n"
        "Он будет активен 1 час.",
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
    await state.set_state(
        CreateOrderStates.order_type
    )

    await callback.message.edit_text(
        "✏️ <b>Изменение параметров</b>\n\n"
        "Выберите тип сделки:",
        reply_markup=order_type_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


# ============================================================
# ОТМЕНА СОЗДАНИЯ
# ============================================================

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


# ============================================================
# МОИ СДЕЛКИ
# ============================================================

@dp.callback_query(
    F.data.startswith("order:pause:")
)
async def pause_order(
    callback: CallbackQuery
):
    order_id = int(
        callback.data.split(":")[2]
    )

    order = orders.get(order_id)

    if not order:
        await callback.answer(
            "Ордер не найден.",
            show_alert=True
        )
        return

    if order["user_id"] != callback.from_user.id:
        await callback.answer(
            "❌ Это не ваш ордер.",
            show_alert=True
        )
        return

    order["active"] = False

    await callback.message.edit_text(
        "⏸️ <b>Ордер отключён.</b>\n\n"
        "Другие пользователи больше не увидят его "
        "в актуальных объявлениях.",
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    F.data.startswith("order:activate:")
)
async def activate_order(
    callback: CallbackQuery
):
    order_id = int(
        callback.data.split(":")[2]
    )

    order = orders.get(order_id)

    if not order:
        await callback.answer(
            "Ордер не найден.",
            show_alert=True
        )
        return

    if order["user_id"] != callback.from_user.id:
        await callback.answer(
            "❌ Это не ваш ордер.",
            show_alert=True
        )
        return

    # Реактивация даёт новый час.
    order["active"] = True
    order["expires_at"] = time.time() + 3600

    await callback.message.edit_text(
        "▶️ <b>Ордер реактивирован.</b>\n\n"
        "Он снова отображается в актуальных объявлениях "
        "на 1 час.",
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    F.data.startswith("order:delete:")
)
async def delete_order(
    callback: CallbackQuery
):
    order_id = int(
        callback.data.split(":")[2]
    )

    order = orders.get(order_id)

    if not order:
        await callback.answer(
            "Ордер уже удалён.",
            show_alert=True
        )
        return

    if order["user_id"] != callback.from_user.id:
        await callback.answer(
            "❌ Это не ваш ордер.",
            show_alert=True
        )
        return

    del orders[order_id]

    await callback.message.edit_text(
        "🗑️ <b>Ордер удалён.</b>",
        parse_mode="HTML"
    )

    await callback.answer()


# ============================================================
# АВТОМАТИЧЕСКОЕ ИСТЕЧЕНИЕ ОРДЕРОВ
# ============================================================

async def order_cleanup_loop():
    while True:
        now = time.time()

        for order in list(orders.values()):
            if (
                order["active"]
                and now >= order["expires_at"]
            ):
                order["active"] = False

        await asyncio.sleep(30)
