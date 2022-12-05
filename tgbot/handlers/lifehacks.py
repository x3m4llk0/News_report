from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from tgbot.dialogs.checkbox import CheckBoxDialog

lifehacks_router = Router()


@lifehacks_router.message(Command(commands=["lifehacks"]))
async def support_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(CheckBoxDialog.state)