from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


keyboard = [
        [KeyboardButton(text="Меню")]
    ]


start_menu = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)