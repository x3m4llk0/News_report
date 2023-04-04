from aiogram import Router, types, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram.filters import Command, Text
from tgbot.dialogs.checkbox import CheckBoxDialog, RelizDialog

lifehacks_router = Router()



@lifehacks_router.callback_query(Text('lifehacks'))
async def lifehacks_menu(call: types.CallbackQuery, bot: Bot):
    lifehacks_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Корректировка контента', callback_data='content')],
            [InlineKeyboardButton(text='Отправка релиза по почте', callback_data='reliz')],
            [InlineKeyboardButton(text='Выход', callback_data='quit_lf')]
        ]
    )
    # await bot.send_message(chat_id=call.from_user.id, text='Выберите нужный:', reply_markup=lifehacks_menu)
    await call.message.edit_text(text='Выберите нужный:', reply_markup=lifehacks_menu)



@lifehacks_router.callback_query(Text('content'))
async def support_handler(call: types.CallbackQuery, dialog_manager: DialogManager):
    await call.answer(cache_time=1)
    await dialog_manager.start(CheckBoxDialog.state)



@lifehacks_router.callback_query(Text('reliz'))
async def support_handler(call: types.CallbackQuery, dialog_manager: DialogManager):
    await call.answer(cache_time=1)
    await dialog_manager.start(RelizDialog.state_reliz)



@lifehacks_router.callback_query(Text('quit_lf'))
async def quit(call: types.CallbackQuery, bot: Bot):
    await call.message.delete()
    await bot.send_message(chat_id=call.from_user.id, text="Вы вышли из лайфхаков ⚠")