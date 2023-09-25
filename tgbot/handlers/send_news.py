from typing import Any

from aiogram import Router, types, Bot
from aiogram.filters import Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
# from aiogram.types import Message, CallbackQuery, Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile
from aiogram.utils.markdown import hbold

from tgbot.keyboards.inline import rules_kb, menu_kb, back_to_menu_kb, approve_disable_bot
from tgbot.keyboards.news_callback import NewsCallBack, NewsTaskCallBack
from tgbot.misc.platform_api import send_upd, send_to_api
from tgbot.misc.questions import questions_and_answers

from tgbot.misc.states import dialog, send_news
from tgbot.models import db_commands as commands



send_news_router = Router()


# from .main_menu import main_menu_router
# send_news_router.include_router(main_menu_router)


@send_news_router.callback_query(Text('send_news'))
async def add_photo(call: types.CallbackQuery, state: FSMContext):
    user = await commands.select_user(call.from_user.id)
    if not user or not user.is_active:
        await call.message.answer(text='Для отправки новости на согласование зарегистрируйся по команде /start')
    else:
        quit_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
        message_id = await call.message.edit_text(text='Пришлите фото новости 📷', reply_markup=quit_markup)

        await state.update_data(message_id=message_id.message_id)
        await state.set_state(send_news.photo)


@send_news_router.message(send_news.photo, F.photo)
async def add_text(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get('message_id'))
    photo_file_id = message.photo[-1].file_id
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Добавить текст 📝', callback_data='add_text')
    button_2 = InlineKeyboardButton(text='Добавить фото 📷', callback_data='add_photo')
    button_3 = InlineKeyboardButton(text='Отменить', callback_data='quit_sn')
    keyboard.row(button_1, button_2)
    keyboard.row(button_3)
    message_id = await message.answer(text='Что нужно добавить к фото?', reply_markup=keyboard.as_markup())
    await state.update_data(message_id=message_id.message_id, photo=photo_file_id)


@send_news_router.callback_query(Text('add_text'))
async def add_text(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data.get('message_id'))
    quit_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
    message_id = await bot.send_message(chat_id=call.from_user.id, text='Введите описание задачи и новости:',
                                        reply_markup=quit_markup)
    await state.update_data(message_id=message_id.message_id)
    await state.set_state(send_news.text)


@send_news_router.message(send_news.text)
async def mailing_text(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get('message_id'))
    text = message.text
    photo = data.get('photo')
    markup = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Отправить ⏱', callback_data='send_with_text'),
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


@send_news_router.callback_query(Text('send_with_text'))
async def start(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)
    sender = await commands.select_user(call.from_user.id)
    agreement_id = await commands.all_users_by_sop_and_agreement(sender.sop)
    agreement_id = agreement_id[0]
    data = await state.get_data()
    text = data.get('text')
    text = f'Необходимо согласовать новость.\n' \
           f'Отправитель: <a href="tg://user?id={call.from_user.id}">{sender.first_name} {sender.last_name}</a>\n' \
           f'Суть новости: {text}'
    photo = data.get('photo')
    await state.clear()
    user_id = call.from_user.id
    message_id_user = data.get('message_id_user')
    message_id_agreement = await bot.send_photo(chat_id=agreement_id, photo=photo, caption=text)
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Согласовано',
                                    callback_data=NewsCallBack(user_id=user_id,
                                                               message_id_user=message_id_user,
                                                               message_id_agreement=message_id_agreement.message_id,
                                                               agreement_id=agreement_id,
                                                               reply_answer='agreed').pack())
    button_2 = InlineKeyboardButton(text='Не согласовано',
                                    callback_data=NewsCallBack(user_id=user_id,
                                                               message_id_user=message_id_user,
                                                               message_id_agreement=message_id_agreement.message_id,
                                                               agreement_id=agreement_id,
                                                               reply_answer='denied').pack())

    keyboard.row(button_1, button_2)

    await bot.send_message(chat_id=agreement_id, text="#Ожидает_согласования", reply_markup=keyboard.as_markup())

    await call.message.answer('Новость отправлена на согласование ⏱')


@send_news_router.callback_query(Text('add_photo'))
async def add_task_photo1(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=data.get('message_id'))
    quit_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
    message_id = await bot.send_message(chat_id=call.from_user.id, text='Пришлите фото задачи 📷:',
                                        reply_markup=quit_markup)
    await state.update_data(message_id=message_id.message_id)
    await state.set_state(send_news.task_photo)


@send_news_router.message(send_news.task_photo, F.photo)
async def add_task_photo2(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get('message_id'))
    task_photo = message.photo[-1].file_id
    photo = data.get('photo')
    keyboard = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Отправить ⏱', callback_data='send_with_task'),
                                            InlineKeyboardButton(text='Отменить', callback_data='quit_sn')
                                        ]
                                    ])
    await message.answer_media_group(media=[InputMediaPhoto(media=photo, caption='Подготовлена новость с фото задачи'), InputMediaPhoto(media=task_photo)])
    message_id_user = await message.answer(text='Отправляем на согласование?', reply_markup=keyboard)
    await state.update_data(message_id_user=message_id_user.message_id, task_photo=task_photo)


@send_news_router.callback_query(Text('send_with_task'))
async def start(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    sender = await commands.select_user(call.from_user.id)
    agreement_id = await commands.all_users_by_sop_and_agreement(sender.sop)
    agreement_id = agreement_id[0]
    text = f'Необходимо согласовать новость.\n' \
           f'Отправитель: <a href="tg://user?id={call.from_user.id}">{sender.first_name} {sender.last_name}</a>\n'
    photo = data.get('photo')
    task_photo = data.get("task_photo")
    await state.clear()
    user_id = call.from_user.id
    message_id_user: Any | None = data.get('message_id_user')
    message_id_agreement = await bot.send_media_group(chat_id=agreement_id,
                                                      media=[InputMediaPhoto(media=photo, caption=text),
                                                             InputMediaPhoto(media=task_photo)])
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Согласовано',
                                    callback_data=NewsTaskCallBack(user_id=user_id,
                                                                   message_id_user=message_id_user,
                                                                   message_id_agreement=message_id_agreement[
                                                                       0].message_id+1,
                                                                   agreement_id=agreement_id,
                                                                   reply_answer='agreed').pack())
    button_2 = InlineKeyboardButton(text='Не согласовано',
                                    callback_data=NewsTaskCallBack(user_id=user_id,
                                                                   message_id_user=message_id_user,
                                                                   message_id_agreement=message_id_agreement[
                                                                       0].message_id+1,
                                                                   agreement_id=agreement_id,
                                                                   reply_answer='denied').pack())

    keyboard.row(button_1, button_2)

    await bot.send_message(chat_id=agreement_id, text="#Ожидает_согласования", reply_markup=keyboard.as_markup())

    await call.message.answer('Новость отправлена на согласование ⏱')


# Отправка новости без текста/фото
@send_news_router.callback_query(Text('re_send_news'))
async def re_news(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    quit_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit_sn')]])
    message_id = await call.message.edit_text(text='Пришлите фото новости 📷', reply_markup=quit_markup)
    await state.update_data(message_id=message_id.message_id)
    await state.set_state(send_news.re_sending)


@send_news_router.message(send_news.re_sending, F.photo)
async def re_sending_news(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get('message_id'))
    photo = message.photo[-1].file_id
    keyboard = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Отправить ⏱', callback_data='re_sending_news'),
                                            InlineKeyboardButton(text='Отменить', callback_data='quit_sn')
                                        ]
                                    ])
    message_id_user = await message.answer_photo(photo=photo, caption=f'Направление новости без описания задачи', reply_markup=keyboard)
    await state.update_data(message_id_user=message_id_user.message_id, photo=photo)



@send_news_router.callback_query(Text('re_sending_news'))
async def start(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    sender = await commands.select_user(call.from_user.id)
    agreement_id = await commands.all_users_by_sop_and_agreement(sender.sop)
    agreement_id = agreement_id[0]

    text = f'Необходимо согласовать новость.\n' \
           f'Отправитель: <a href="tg://user?id={call.from_user.id}">{sender.first_name} {sender.last_name}</a>\n' \
           f'Новость отправлена без описания задачи'
    photo = data.get('photo')
    await state.clear()
    user_id = call.from_user.id
    message_id_user = data.get('message_id_user')
    message_id_agreement = await bot.send_photo(chat_id=agreement_id, photo=photo, caption=text)
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Согласовано',
                                    callback_data=NewsCallBack(user_id=user_id,
                                                               message_id_user=message_id_user,
                                                               message_id_agreement=message_id_agreement.message_id,
                                                               agreement_id=agreement_id,
                                                               reply_answer='agreed').pack())
    button_2 = InlineKeyboardButton(text='Не согласовано',
                                    callback_data=NewsCallBack(user_id=user_id,
                                                               message_id_user=message_id_user,
                                                               message_id_agreement=message_id_agreement.message_id,
                                                               agreement_id=agreement_id,
                                                               reply_answer='denied').pack())

    keyboard.row(button_1, button_2)

    await bot.send_message(chat_id=agreement_id, text="#Ожидает_согласования", reply_markup=keyboard.as_markup())

    await call.message.answer('Новость отправлена на согласование ⏱')




@send_news_router.callback_query(NewsCallBack.filter())
async def reply_answer_yes(call: types.CallbackQuery, callback_data: NewsCallBack, state: FSMContext, bot: Bot):
    await call.answer(cache_time=60)
    user_id = callback_data.user_id
    message_id_user = callback_data.message_id_user
    message_id_agreement = callback_data.message_id_agreement
    agreement_id = callback_data.agreement_id

    if callback_data.reply_answer == 'agreed':

        await bot.edit_message_text(text="✅ #Согласовано ✅", message_id=int(message_id_agreement) + 1,
                                    chat_id=agreement_id, reply_markup=None)
        # ответ юзеру что новость согласована
        await bot.send_message(chat_id=user_id, text="✅ Новость согласована ✅", reply_to_message_id=message_id_user)

    elif callback_data.reply_answer == 'denied':
        reason_message_id = await bot.send_message(chat_id=agreement_id, text="Введите причину отказа:",
                                                   reply_to_message_id=message_id_agreement)
        await state.update_data(user_id=user_id, agreement_id=agreement_id,
                                message_id_user=message_id_user, message_id_agreement=message_id_agreement,
                                reason_message_id=reason_message_id.message_id)
        await state.set_state(send_news.reason)


@send_news_router.message(send_news.reason)
async def mailing_text(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text
    data = await state.get_data()
    user_id = data.get('user_id')
    message_id_user = data.get('message_id_user')
    agreement_id = data.get('agreement_id')
    message_id_agreement = data.get('message_id_agreement')
    reason_message_id = data.get('reason_message_id')
    await message.answer("Ваши комментарии отправлены")
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Отправить новую новость', callback_data='send_news')
    button_2 = InlineKeyboardButton(text='Повторить новость без описания', callback_data='re_send_news')
    keyboard.row(button_1)
    keyboard.row(button_2)

    await bot.send_message(chat_id=user_id, reply_to_message_id=message_id_user,
                           text=f"❌ Новость не согласована❌ Комментрии:\n"
                                f"{text}\n"
                                f"Вы можете сформировать новую новость или, с учетом комментариев, повторить отправку новости без описания", reply_markup=keyboard.as_markup())
    await bot.edit_message_text(text="❌ #Не_согласовано ❌", message_id=int(message_id_agreement) + 1,
                                chat_id=agreement_id, reply_markup=None)
    await bot.delete_message(chat_id=agreement_id, message_id=int(reason_message_id))
    await state.clear()




