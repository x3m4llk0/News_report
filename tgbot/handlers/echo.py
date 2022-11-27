from aiogram import types, Router, F
from aiogram.utils.markdown import hbold
from aiogram import Bot
from loader import bot
echo_router = Router()


@echo_router.message(F.text, F.via_bot == None, state=None)
async def bot_echo(message: types.Message):
    text = [
        f"Команды {hbold(message.text)} нет.\n",
        f"Кажется, вы слегка промахнулись. С кем не бывает! ",
        f"Для возврата в главное меню нажмите /menu",
    ]
    await message.answer('\n'.join(text))



async def send_message(bot: Bot, user_id, text: str, disable_notification: bool = False) -> bool:
    await bot.send_message(user_id, text, disable_notification=disable_notification)