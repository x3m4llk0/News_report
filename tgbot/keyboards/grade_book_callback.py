from aiogram.filters.callback_data import CallbackData

class SendBonusMistake(CallbackData, prefix="send_bonus_mistake"):
    employee: int
    gb_type: str

class UpdateBonusMistake(CallbackData, prefix="update_bonus_mistake"):
    gb_type: str
    id: int
    comment: str


class SendMistake(CallbackData, prefix="send_mistake"):
    user_id: int

class SendLike(CallbackData, prefix="send_like"):
    employee: int
