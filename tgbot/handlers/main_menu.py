from aiogram import Router, types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from tgbot.models import db_commands as commands
# from aiogram.types import Message, CallbackQuery, Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile

from .send_news import send_news_router
from .lifehacks import lifehacks_router
from .admin import admin_router
from .grade_book import grade_book_router



main_menu_router = Router()

main_menu_router.include_router(send_news_router)
main_menu_router.include_router(lifehacks_router)
main_menu_router.include_router(admin_router)
main_menu_router.include_router(grade_book_router)


@main_menu_router.message(F.text == "Меню")
async def test(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Отправить новость', callback_data='send_news')
    button_2 = InlineKeyboardButton(text='Лайфхаки', callback_data='lifehacks')
    button_3 = InlineKeyboardButton(text='Карта бонусов #в работе', callback_data='grade_book')
    button_4 = InlineKeyboardButton(text='Помощь', callback_data='help')
    button_5 = InlineKeyboardButton(text='Вернуть согласование', callback_data='ca_to_return')
    button_6 = InlineKeyboardButton(text='Изменить должность', callback_data='changerole')
    button_7 = InlineKeyboardButton(text='Передать согласование', callback_data='changeaccess')
    button_8 = InlineKeyboardButton(text='О секторе', callback_data='my_team')

    user = await commands.select_user(message.from_user.id)
    if not user or user.status != "active":
        await message.answer(text='Для использования бота зарегистрируйся по команде /start')
    else:
        if message.from_user.id in await commands.all_users_by_role('ns'): #НСы
            keyboard.row(button_8, button_6)
            keyboard.row(button_7, button_5)
            keyboard.row(button_3)
            keyboard.row(button_4)
            await message.answer(text='Выберите функцию', reply_markup=keyboard.as_markup())

        elif message.from_user.id in await commands.all_users_by_access('agreement'): #согласующие
            keyboard.row(button_1) #for test
            keyboard.row(button_5)
            keyboard.row(button_2)
            keyboard.row(button_3)
            keyboard.row(button_4)
            await message.answer(text='Выберите функцию', reply_markup=keyboard.as_markup())

        elif message.from_user.id in await commands.all_users_by_sop('stvp'): # соп СТВП
            keyboard.row(button_1)
            keyboard.row(button_2)
            keyboard.row(button_3)
            keyboard.row(button_4)
            await message.answer(text='Выберите функцию', reply_markup=keyboard.as_markup())
        else: #остальные сотрудники
            keyboard.row(button_1)
            keyboard.row(button_2)
            keyboard.row(button_4)
            await message.answer(text='Выберите функцию', reply_markup=keyboard.as_markup())




