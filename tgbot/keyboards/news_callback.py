from aiogram.filters.callback_data import CallbackData
from typing import Optional

class NewsCallBack(CallbackData, prefix="news"):
    user_id: str
    message_id_user: Optional[str]
    message_id_superuser: Optional[str]
    superuser_id: Optional[str]
    reply_answer: Optional[str]


class ChangeRoleCB(CallbackData, prefix="change_role"):
    user_id: int
    new_role: str


class ChangeAccessCB(CallbackData, prefix="change_role"):
    user_id: int
