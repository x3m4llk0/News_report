from aiogram.fsm.state import StatesGroup, State


class registration(StatesGroup):
    first_name = State()
    last_name = State()


class dialog(StatesGroup):
    session = State()

class send_news(StatesGroup):
    text = State()
    photo = State()
    send = State()
    reason = State()
