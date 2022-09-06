from aiogram import types, Router, F

echo_router = Router()


@echo_router.message(F.text, state=None)
async def bot_echo(message: types.Message):
    text = [
        "Ехо без стану.",
        "Повідомлення:",
        message.text
    ]

    await message.answer('\n'.join(text))


