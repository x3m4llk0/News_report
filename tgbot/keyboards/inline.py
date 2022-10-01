from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def rules_kb():
    kb = InlineKeyboardBuilder()
    rules = InlineKeyboardButton(text="Правила Программы",
                                 url="https://promo.splatglobal.com/wp-content/landings/ambassador/upload/rules.pdf")
    policy = InlineKeyboardButton(text="Политику конфиденциальности ",
                                  url="https://promo.splatglobal.com/wp-content/landings/ambassador/upload/policy.pdf")
    accept = InlineKeyboardButton(text="✅ Принять", callback_data="accept_rules")
    cancel = InlineKeyboardButton(text="❌ Отказаться", callback_data="cancel_rules")
    kb.row(rules)
    kb.row(policy)
    kb.row(accept, cancel)
    return kb.as_markup()


async def menu_kb():
    kb = InlineKeyboardBuilder()
    button_4 = InlineKeyboardButton(text="Программа «ДРУЗЬЯ SPLAT»", switch_inline_query_current_chat="#Программа")
    button_1 = InlineKeyboardButton(text="Продукция", switch_inline_query_current_chat="#Продукция")
    button_5 = InlineKeyboardButton(text="Техподдержка", callback_data="another_question")
    button_6 = InlineKeyboardButton(text="❌ Покинуть Сообщество", callback_data="disable_bot_approve")
    kb.row(button_4)
    kb.row(button_5)
    kb.row(button_1)
    kb.row(button_6)
    return kb.as_markup()


async def back_to_menu_kb():
    kb = InlineKeyboardBuilder()
    button = InlineKeyboardButton(text="⬅️ Возврат в Меню", callback_data="back_to_menu")
    kb.row(button)
    return kb.as_markup()


async def approve_disable_bot():
    kb = InlineKeyboardBuilder()
    yes = InlineKeyboardButton(text="🥲 Да", callback_data="disable_bot")
    no = InlineKeyboardButton(text="🥳 Нет", callback_data="not_disable_bot")
    kb.row(yes, no)
    return kb.as_markup()
