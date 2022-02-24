from aiogram.dispatcher.filters.state import State, StatesGroup


class Update(StatesGroup):

    name = State()
    phone = State()
    email = State()
    location = State()