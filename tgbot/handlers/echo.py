from aiogram import types, Router, F
from aiogram.utils.markdown import hbold

echo_router = Router()


@echo_router.message(F.text, state=None)
async def bot_echo(message: types.Message):
    text = [
        [
            f"Команды {hbold(message.text)} нету.\n",
            f"Для просмотра команд выполните команду /menu либо /start",
        ]
    ]

    await message.answer('\n'.join(text))


