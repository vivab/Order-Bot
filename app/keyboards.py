from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="💱 Торговля", callback_data="menu:trading")
    builder.button(text="👤 Профиль", callback_data="menu:profile")
    builder.button(text="🛡️ Актуальные гаранты", callback_data="menu:guarantors")

    builder.adjust(1)
    return builder.as_markup()


def trading_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text="🟢 Купить", callback_data="trading:buy")
    builder.button(text="🔴 Продать", callback_data="trading:sell")
    builder.button(text="📋 Мои сделки", callback_data="trading:my")
    builder.button(text="➕ Создать сделку", callback_data="trading:create")
    builder.button(text="◀️ Назад", callback_data="menu:main")

    builder.adjust(2, 1, 1)
    return builder.as_markup()


def back_main():
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Главное меню", callback_data="menu:main")
    return builder.as_markup()


def order_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔴 Продать крипту",
        callback_data="order_type:sell"
    )

    builder.button(
        text="🟢 Купить крипту",
        callback_data="order_type:buy"
    )

    builder.button(
        text="❌ Отмена",
        callback_data="order:cancel"
    )

    builder.adjust(1)
    return builder.as_markup()


def fiat_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="🇷🇺 RUB", callback_data="fiat:RUB")
    builder.button(text="🇺🇦 UAH", callback_data="fiat:UAH")
    builder.button(text="🇧🇾 BYN", callback_data="fiat:BYN")
    builder.button(text="🇰🇿 KZT", callback_data="fiat:KZT")

    builder.button(
        text="❌ Отмена",
        callback_data="order:cancel"
    )

    builder.adjust(2)
    return builder.as_markup()


def coin_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="₮ USDT", callback_data="coin:USDT")
    builder.button(text="💎 TON", callback_data="coin:TON")
    builder.button(text="🟣 SOL", callback_data="coin:SOL")
    builder.button(text="₿ BTC", callback_data="coin:BTC")
    builder.button(text="♦️ ETH", callback_data="coin:ETH")

    builder.button(
        text="❌ Отмена",
        callback_data="order:cancel"
    )

    builder.adjust(2)
    return builder.as_markup()


def conditions_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⏭️ Без условий",
        callback_data="conditions:none"
    )

    builder.button(
        text="❌ Отмена",
        callback_data="order:cancel"
    )

    builder.adjust(1)
    return builder.as_markup()


def confirmation_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✏️ Изменить параметры",
        callback_data="order:edit"
    )

    builder.button(
        text="🚀 Опубликовать сделку",
        callback_data="order:publish"
    )

    builder.button(
        text="❌ Отмена",
        callback_data="order:cancel"
    )

    builder.adjust(1)
    return builder.as_markup()
