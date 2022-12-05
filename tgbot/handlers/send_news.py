from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
# from aiogram.types import Message, CallbackQuery, Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile
from aiogram.utils.markdown import hbold

from tgbot.keyboards.inline import rules_kb, menu_kb, back_to_menu_kb, approve_disable_bot
from tgbot.keyboards.news_callback import NewsCallBack
from tgbot.misc.platform_api import send_upd, send_to_api
from tgbot.misc.questions import questions_and_answers

from tgbot.misc.states import dialog, send_news
from tgbot.models import db_commands as commands

send_news_router = Router()


@send_news_router.message(Command("news"))
async def add_photo(message: types.Message, state: FSMContext):
    user = await commands.select_user(message.from_user.id)
    if not user or user.status != "active":
        await message.answer(text='Для отправки новости на согласование зарегистрируйся по команде /start')
    else:
        quit_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
        await message.answer(text='Пришлите фото новости', reply_markup=quit_markup)
        await state.set_state(send_news.photo)


@send_news_router.message(send_news.photo, F.photo)
async def add_text(message: types.Message, state: FSMContext):

    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    quit_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
    await message.answer(text='Введите описание задачи и новости:', reply_markup=quit_markup)
    await state.set_state(send_news.text)


@send_news_router.message(send_news.text)
async def mailing_text(message: types.Message, state: FSMContext):
    await message.delete_reply_markup()
    data = await state.get_data()
    text = message.text
    photo = data.get('photo')
    markup = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Отправить ⏱', callback_data='next'),
                                          InlineKeyboardButton(text='Отменить', callback_data='quit_sn')
                                      ]
                                  ])
    message_id_user = await message.answer_photo(photo=photo, caption=f'Суть новости: {text}', reply_markup=markup)
    await state.update_data(text=text, message_id_user=message_id_user.message_id)


@send_news_router.callback_query(Text('quit_sn'))
async def quit(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.message.delete()
    await bot.send_message(chat_id=call.from_user.id, text="Вы отменили согласование новости ⚠")






@send_news_router.callback_query(Text('next'))
async def start(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)
    users = await commands.user_rights_access()
    data = await state.get_data()
    sender = await commands.select_user(call.from_user.id)

    text = data.get('text')
    text = f'Необходимо согласовать новость.\n' \
           f'Отправитель: <a href="tg://user?id={call.from_user.id}">{sender.first_name} {sender.last_name}</a>\n' \
           f'Суть новости: {text}'
    photo = data.get('photo')
    await state.clear()
    for user in users:
        user_id = call.from_user.id
        superuser_id = user.user_id
        message_id_user = data.get('message_id_user')
        message_id_superuser = await bot.send_photo(chat_id=user.user_id, photo=photo, caption=text)

        # отправка группы фото
        # await bot.send_media_group(chat_id=user.user_id, media=[InputMediaPhoto(media=photo, caption=text),InputMediaPhoto(media=photo)])

        keyboard = InlineKeyboardBuilder()

        button_1 = InlineKeyboardButton(text='Согласовано',
                                        callback_data=NewsCallBack(user_id=user_id,
                                                                   message_id_user=message_id_user,
                                                                   message_id_superuser=message_id_superuser.message_id,
                                                                   superuser_id=superuser_id,
                                                                   reply_answer='agreed').pack())
        button_2 = InlineKeyboardButton(text='Не согласовано',
                                        callback_data=NewsCallBack(user_id=user_id,
                                                                   message_id_user=message_id_user,
                                                                   message_id_superuser=message_id_superuser.message_id,
                                                                   superuser_id=superuser_id,
                                                                   reply_answer='denied').pack())

        keyboard.row(button_1, button_2)

        await bot.send_message(chat_id=user.user_id, text="#Ожидает_согласования", reply_markup=keyboard.as_markup())

    await call.message.answer('Новость отправлена на согласование ⏱')


@send_news_router.callback_query(NewsCallBack.filter())
async def reply_answer_yes(call: types.CallbackQuery,callback_data: NewsCallBack, state: FSMContext, bot: Bot):
    await call.answer(cache_time=60)
    user_id = callback_data.user_id
    message_id_user = callback_data.message_id_user
    message_id_superuser = callback_data.message_id_superuser
    superuser_id = callback_data.superuser_id

    if callback_data.reply_answer == 'agreed':
        # callback_data = call.data.split(":")
        #Изменение текста запроса на согласование и удаление кейборда
        await bot.edit_message_text(text="✅ #Согласовано ✅", message_id=int(message_id_superuser)+1, chat_id=superuser_id, reply_markup=None)
        # ответ юзеру что новость согласована
        await bot.send_message(chat_id=user_id, text="✅ Новость согласована ✅", reply_to_message_id=message_id_user)

    elif callback_data.reply_answer == 'denied':
        reason_message_id = await bot.send_message(chat_id=superuser_id, text="Введите причину отказа:",
                                                      reply_to_message_id=message_id_superuser)
        await state.update_data(user_id=user_id, superuser_id=superuser_id,
                                message_id_user=message_id_user, message_id_superuser=message_id_superuser,
                                reason_message_id=reason_message_id.message_id)
        await state.set_state(send_news.reason)


@send_news_router.message(send_news.reason)
async def mailing_text(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text
    data = await state.get_data()
    user_id = data.get('user_id')
    message_id_user = data.get('message_id_user')
    superuser_id = data.get('superuser_id')
    message_id_superuser = data.get('message_id_superuser')
    reason_message_id = data.get('reason_message_id')
    await message.answer("Ваши комментарии отправлены")
    await bot.send_message(chat_id=user_id, reply_to_message_id=message_id_user,
                              text=f"❌ Новость не согласована❌ Комментрии:\n"
                                   f"{text}\n"
                                   f"Для отправки новой новости нажмите /news")
    await bot.edit_message_text(text="❌ #Не_согласовано ❌", message_id=int(message_id_superuser)+1, chat_id=superuser_id, reply_markup=None)
    await bot.delete_message(chat_id=superuser_id, message_id=int(reason_message_id))
    await state.clear()