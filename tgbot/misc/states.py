from aiogram.fsm.state import StatesGroup, State


class registration(StatesGroup):
    first_name = State()
    last_name = State()
    role = State()
    finnaly = State()


class dialog(StatesGroup):
    session = State()

class send_news(StatesGroup):
    text = State()
    photo = State()
    send = State()
    reason = State()
    task_photo = State()
    re_sending = State()

class send_bonus(StatesGroup):
    activity = State()
    criterion = State()
    quarter = State()
    confirmation = State()
    comment = State()

class add_comment(StatesGroup):
    add_comment = State()
