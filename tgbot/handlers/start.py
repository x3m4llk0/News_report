from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.types import Message, CallbackQuery, Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile
from aiogram.utils.markdown import hbold

from loader import config
from tgbot.keyboards.inline import rules_kb, menu_kb, back_to_menu_kb, approve_disable_bot
from tgbot.misc.platform_api import send_upd, send_to_api
from tgbot.misc.questions import questions_and_answers
from tgbot.misc.states import dialog, registration
from tgbot.models import db_commands as commands

user_router = Router()


@user_router.message(commands=["start"], state=None)
async def bot_start(message: types.Message, state: FSMContext, bot: Bot):
    user = await commands.select_user(message.from_user.id)
    if not user or not user.is_active:
        print(await bot.get_updates())
        quit_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Отменить', callback_data='quit')]])

        await message.answer('Приветствую тебя СОПовец! Началась регистрация.\nОтправь мне своё имя:'
                             , disable_web_page_preview=True, parse_mode='Markdown', reply_markup=quit_markup)
        await state.set_state(registration.first_name)
    else:
        if user.status == "active":
            await message.answer(f"Привет {user.first_name}\n"
                                 f"Ты уже зарегистрирован")

        elif user.status == "ban":
            await message.answer("Ты забанен")

        else:
            await message.answer("Обратись к администратору бота @x3m4llk0")


## Продолжение регистрцации
@user_router.message(state=registration.first_name)
async def first_name_user(message: types.Message, state: FSMContext):
    first_name = message.text.capitalize()
    await state.update_data(first_name=first_name)
    await message.answer('Отправь мне свою фамилию:\n')
    await state.set_state(registration.last_name)


@user_router.message(state=registration.last_name)
async def last_name_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    first_name = data.get('first_name')
    last_name = message.text.capitalize()
    await commands.create_user(user_id=message.from_user.id,
                               tg_first_name=message.from_user.first_name,
                               username=message.from_user.username,
                               first_name=first_name,
                               last_name=last_name,
                               access='User',
                               role='analyst',
                               bonus=int('0'),
                               mistake=int('0'),
                               status="active",
                               is_active=True)
    await message.answer(f"Ты успешно зарегистрирован!\n"
                         "Чтобы узнать мои возможности нажми /help")
    await state.clear()


@user_router.callback_query(text='quit', state=[registration.last_name, registration.first_name])
async def quit(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.message.delete()
    await bot.send_message(chat_id=call.from_user.id, text="Вы отменили регистрацию ⚠")


@user_router.message(commands=["help"], state=None)
async def help(message: types.Message):
    user = await commands.select_user(user_id=message.from_user.id)
    if user.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids:
        await message.answer(f"Вам доступны следующие команды:\n"
                             f"/changerole - позволяет назначать экспертов и аналитиков\n"
                             f"/changeaccess - позволяет назначать заместителя для согласований\n"
                             f"/my_team - показывает информацию о сотрудниках\n"
                             f"/my_team_export - выгружает инфо о сотрудниках в файле")
    elif user.access == 'SuperUser':
        await message.answer(f'Вам доступны следующие команды:\n'
                             f"/changeacces - позволяет назначать нового заместителя для согласований или вернуть согласование НС")
    else:
        await message.answer(f"Вам доступны следующие команды:\n"
                             f"/news - позволяет отправлять новость на согласование")

# @user_router.message(commands=["start"], state=None)
# async def user_start(message: types.Message):
#     user = await commands.select_user(message.chat.id)
#     if not user or not user.is_active:
#         await commands.create_user(user_id=message.from_user.id,
#                                    tg_first_name=message.from_user.first_name,
#                                    username=message.from_user.username,
#                                    first_name="Имя",
#                                    last_name="Фамилия",
#                                    access='User',
#                                    role='user',
#                                    bonus=int('0'),
#                                    mistake=int('0'),
#                                    status="active",
#                                    is_active=True)
#         await message.answer("Ты зарегистрирован")
#     else:
#         await message.answer("Ты уже зареган")

# @user_router.message(commands=["start"], state=None)
# async def user_start(message: Message):
#     user = await get_user(message.chat.id)
#     if not user or not user.is_active:
#         return await message.answer(hbold(
#             f'Привет! Мы рады видеть вас в чате-боте «Друзья SPLAT»! Нажимая на кнопку'
#             f'«Принять», вы соглашаетесь с Правилами Программы и '
#             f'даете согласие на обработку ваших персональных данных, согласно Политике конфиденциальности.'
#         ), reply_markup=await rules_kb())
#     await message.answer("Выберите нужный пункт меню 👇", reply_markup=await menu_kb())
#
#
#
# @user_router.message(commands=["menu"], state=None)
# async def user_start(message: Message):
#     user = await get_user(message.chat.id)
#     if not user or not user.is_active:
#         return await message.answer(hbold(
#             f'Привет! Мы рады видеть вас в чате-боте «Друзья SPLAT»! Нажимая на кнопку'
#             f'«Принять», вы соглашаетесь с Правилами Программы и '
#             f'даете согласие на обработку ваших персональных данных, согласно Политике конфиденциальности.'
#         ), reply_markup=await rules_kb())
#     await message.answer("Выберите нужный пункт меню 👇", reply_markup=await menu_kb())
#
#
# @user_router.callback_query(text="rules")
# async def rules(call: CallbackQuery):
#     file = FSInputFile(f'rules_friends.pdf')
#     await call.message.answer_document(document=file)
#
#
# @user_router.message(commands=["stop_dialog"])
# async def stop_dialog(message: Message, state: FSMContext, event_update: Update):
#     await state.clear()
#     await send_upd(event_update.json(), close_session=True)
#     await message.answer(
#         "Ваше обращение принято, сессия завершена. Можете пользоваться ботом дальше (Возврат в меню)",
#         reply_markup=await back_to_menu_kb())
#
#
# @user_router.callback_query(text="accept_rules")
# async def accept_rules(call: CallbackQuery):
#     await create_user(call.message.chat.id, username=call.message.chat.username, is_active=True)
#     await send_to_api(call.message.chat.id, title="Подтвердил правила", name="start")
#     await call.message.edit_text("\n".join(
#         [
#             f'{hbold("Ура, спасибо, что вы с нами!")}',
#             f'Добро пожаловать в клуб «Друзей SPLAT»! Вот ссылка на наш закрытый канал: '
#             f'https://t.me/+dCKPtkvgTvY5OWEy. Подпишитесь на него – именно там будут '
#             f'происходить все основные активности.'
#         ]
#     ), reply_markup=await menu_kb(), disable_web_page_preview=True)
#
#
# @user_router.callback_query(text="back_to_menu", state="*")
# async def back_to_menu(call: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await send_to_api(call.message.chat.id)
#     await call.message.edit_text("Выберите нужный пункт меню 👇", reply_markup=await menu_kb())
#
#
# @user_router.callback_query(text="cancel_rules")
# async def cancel_rules(call: CallbackQuery):
#     await send_to_api(call.message.chat.id)
#     await send_to_api(call.message.chat.id, title="Отклонил правила", name="cancel_rules")
#     await call.message.edit_text("Жаль, что вы не с нами! Но если передумаете, то возвращайтесь, нажав /start")
#
#
# @user_router.callback_query(text="disable_bot_approve")
# async def cancel_rules(call: CallbackQuery):
#     await call.message.edit_text("Что 😮?! Вы серьезно хотите нас покинуть?", reply_markup=await approve_disable_bot())
#
#
# @user_router.callback_query(text="disable_bot")
# async def cancel_rules(call: CallbackQuery):
#     await delete_user(call.message.chat.id)
#     await send_to_api(call.message.chat.id, title="Покинул бота", name="disable_bot")
#     await call.message.edit_text("Что ж, не смеем вас больше задерживать, но будем скучать без вас 😢!")
#
#
# @user_router.callback_query(text="not_disable_bot")
# async def cancel_rules(call: CallbackQuery):
#     await call.message.edit_text("Как мы рады, что вы остаетесь с нами! \n"
#                                  "Забудем о былом, возвращайтесь скорее в главное меню",
#                                  reply_markup=await back_to_menu_kb())
#
#
# @user_router.callback_query(text="another_question")
# async def another_question(call: CallbackQuery, state: FSMContext):
#     await call.message.edit_text("Не нашли ответ на свой вопрос? \n\n"
#                                  "Напишите его нам в окошке сообщений. Мы обязательно вернемся к вам с ответом!)",
#                                  reply_markup=await back_to_menu_kb())
#     await state.set_state(dialog.session)
#     await state.update_data(count=0)
#
#
# @user_router.message(state=dialog.session)
# async def dialog_with_manager(message: Message, event_update: Update, state: FSMContext):
#     session = await get_session(user_id=message.chat.id)
#     await send_to_api(message.chat.id)
#     data = await state.get_data()
#     count = data.get("count")
#     if message.text:
#         if message.text.startswith("/"):
#             return message.answer(
#                 f"Для продолжения работы нажмите /stop_dialog")
#     if session:
#         await send_upd(event_update.json())
#     else:
#         await send_upd(event_update.json(), True)
#         await create_session(user_id=message.chat.id)
#     if count == 0:
#         await message.answer("Спасибо за ваш вопрос! Мы отправили его менеджеру, "
#                              "он свяжется с вами скоро! Для остановки чата нажмите /stop_dialog")
#         await state.update_data(count=1)
#
#
# @user_router.inline_query(text="#Продукция")
# @user_router.inline_query(text="#Программа")
# async def show_question(query: InlineQuery):
#     user_id = query.from_user.id
#     user = await get_user(user_id)
#     if not user or not user.is_active:
#         await query.answer(
#             results=[],
#             switch_pm_text="Бот недоступен. Перейдите в боте и примите правила.",
#             switch_pm_parameter="inline",
#             cache_time=5
#         )
#         return
#     if query.query == "#Продукция":
#         name = "question"
#         photo_url = "https://i.imgur.com/eyU7EDv.png"
#     else:
#         name = "program_inline"
#         photo_url = "https://i.imgur.com/OvIeJEg.png"
#     await send_to_api(user_id, title=f"Запрос по тематике {query.query}", name=name)
#     Q_A = await questions_and_answers(query.query)
#     result = []
#     for number, item in enumerate(Q_A, start=1):
#         result.append(InlineQueryResultArticle(id=number,
#                                                title=item,
#                                                input_message_content=InputTextMessageContent(
#                                                    message_text=f'{hbold(item)}\n\n' + Q_A[item],
#                                                    disable_web_page_preview=True,
#                                                ),
#                                                thumb_url=photo_url,
#                                                description=Q_A[item][:20] + "..."
#                                                ))
#     await query.answer(results=result)
