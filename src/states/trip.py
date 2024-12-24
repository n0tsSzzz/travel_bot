from aiogram.fsm.state import State, StatesGroup


class CreateTripForm(StatesGroup):
    title = State()
    days = State()
    items = State()
    finish = State()
