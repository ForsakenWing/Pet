from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):

    start = State()
    callback = State()
    name = State()
    phone = State()
    choose = State()
    email = State()
    second_choose = State()
    location = State()
    finish = State()