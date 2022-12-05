from aiogram import types, Router, F
from aiogram.filters import Text
from aiogram.utils.markdown import hbold
from aiogram import Bot

echo_router = Router()


@echo_router.message()
async def bot_echo(message: types.Message):
    text = [
        f"Команды {hbold(message.text)} нет.\n",
        f"Кажется, вы слегка промахнулись. С кем не бывает! ",
        f"Для возврата в главное меню нажмите /help",
    ]
    await message.answer('\n'.join(text))


async def send_message(bot: Bot, user_id, text: str, disable_notification: bool = False) -> bool:
    await bot.send_message(user_id, text, disable_notification=disable_notification)
