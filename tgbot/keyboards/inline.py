from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def rules_kb():
    kb = InlineKeyboardBuilder()
    accept = InlineKeyboardButton(text="✅ Принять", callback_data="accept_rules")
    cancel = InlineKeyboardButton(text="❌ Отказаться", callback_data="cancel_rules")
    kb.add(accept, cancel)
    return kb.as_markup()


async def menu_kb():
    kb = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text="Продукция", switch_inline_query_current_chat="#Продукция")
    button_2 = InlineKeyboardButton(text="Поддержка", switch_inline_query_current_chat="#Поддержка")
    button_3 = InlineKeyboardButton(text="Информация", switch_inline_query_current_chat="#Информация")
    button_4 = InlineKeyboardButton(text="Предложение", switch_inline_query_current_chat="#Предложение")
    button_5 = InlineKeyboardButton(text="Задать свой вопрос", callback_data="another_question")
    button_6 = InlineKeyboardButton(text="❌ Выйти из программы", callback_data="disable_bot")
    kb.row(button_1)
    kb.row(button_2)
    kb.row(button_3)
    kb.row(button_4)
    kb.row(button_5)
    kb.row(button_6)
    return kb.as_markup()


async def back_to_menu_kb():
    kb = InlineKeyboardBuilder()
    button = InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
    kb.row(button)
    return kb.as_markup()
