from aiogram.fsm.state import State, StatesGroup


class CreateOrderStates(StatesGroup):
    order_type = State()
    fiat = State()
    coin = State()
    amount = State()
    rate = State()
    conditions = State()
    confirmation = State()
