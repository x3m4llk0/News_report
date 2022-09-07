from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.callback_data import ProductsCallback
from tgbot.misc.questions import products_questions


async def rules_kb():
    kb = InlineKeyboardBuilder()
    accept = InlineKeyboardButton(text="✅ Принять", callback_data="accept_rules")
    cancel = InlineKeyboardButton(text="❌ Отказаться", callback_data="cancel_rules")
    kb.add(accept, cancel)
    return kb.as_markup()


async def menu_kb():
    kb = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text="Продукция", callback_data="products")
    button_2 = InlineKeyboardButton(text="Поддержка", callback_data="accept_rules")
    button_3 = InlineKeyboardButton(text="Информация", callback_data="accept_rules")
    button_4 = InlineKeyboardButton(text="Предложение", callback_data="accept_rules")
    button_5 = InlineKeyboardButton(text="❌ Выйти из программы", callback_data="disable_bot")
    kb.row(button_1)
    kb.row(button_2)
    kb.row(button_3)
    kb.row(button_4)
    kb.row(button_5)
    return kb.as_markup()


async def product_kb():
    kb = InlineKeyboardBuilder()
    for number, question in enumerate(products_questions()):
        button = InlineKeyboardButton(text=question, callback_data=ProductsCallback(id=number).pack())
        kb.row(button)
    button_2 = InlineKeyboardButton(text="Задать свой вопрос", callback_data="another_question")
    button_3 = InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
    kb.row(button_2)
    kb.row(button_3)
    return kb.as_markup()


async def back_to_menu_kb():
    kb = InlineKeyboardBuilder()
    button = InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
    kb.row(button)
    return kb.as_markup()
