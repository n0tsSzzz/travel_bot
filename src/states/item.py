from aiogram.fsm.state import State, StatesGroup


class CreateItemForm(StatesGroup):
    title = State()
