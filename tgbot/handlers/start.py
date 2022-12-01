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
    if not user or user.status != "active":
        await message.answer(text='Для работы с ботом зарегистрируйся по команде /start')
    else:
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



@user_router.message(commands=["lifehacks"], state=None)
async def lifehacks(message: types.Message):
