from aiogram.filters import Command, Text
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Bot, F, types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from aiogram.types import Message, CallbackQuery, Update, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile
from aiogram.utils.markdown import hbold


from loader import config

from tgbot.keyboards.inline import rules_kb, menu_kb, back_to_menu_kb, approve_disable_bot
from tgbot.misc.platform_api import send_upd, send_to_api
from tgbot.misc.questions import questions_and_answers
from tgbot.misc.states import dialog, registration
from tgbot.models import db_commands as commands

from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog import DialogRegistry
from aiogram_dialog import Dialog

from tgbot.keyboards.reply import start_menu


user_router = Router()
role_dict = {'analyst': 'Аналитик', 'expert': 'Эксперт', 'ns': 'Начальник сектора'}
sop_dict = {'stvp': 'Ставрополь', 'omsk': 'Омск', 'vlg': 'Волгоград', 'smr': 'Самара'}

@user_router.message((Command(commands=["start"])))
async def bot_start(message: types.Message, state: FSMContext, bot: Bot):
    user = await commands.select_user(message.from_user.id)
    if not user:
    # if not user or not user.is_active:
        register_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='СТВП', callback_data='sop_stvp'),
                    InlineKeyboardButton(text='Омск', callback_data='sop_omsk'),
                    InlineKeyboardButton(text='ВЛГ', callback_data='sop_vlg'),
                    InlineKeyboardButton(text='СМР', callback_data='sop_smr'),
                 ],
                [InlineKeyboardButton(text='Отменить', callback_data='quit')]
            ])

        await message.answer('Приветствую тебя СОПовец! Началась регистрация.\nВыбери свой город:'
                             , disable_web_page_preview=True, parse_mode='Markdown', reply_markup=register_markup)

    else:
        if user.status == "active":
            await message.answer(f"Привет {user.first_name}\n"
                                 f"Ты уже зарегистрирован", reply_markup=start_menu)
        elif user.status == "ban":
            await message.answer("Ты забанен")

        else:
            await message.answer("Обратись к администратору бота @x3m4llk0")


# Регистрцации после выбора сопа
@user_router.callback_query(Text(contains='sop_'))
async def choise_sop(call: CallbackQuery, bot: Bot, state: FSMContext):
    sop = call.data[4:]
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(text=f'Вы выбрали: {sop_dict[sop]}')

    await state.update_data(sop=sop)
    await bot.send_message(text='Отправь мне cвое имя:\n', chat_id=call.from_user.id)
    await state.set_state(registration.first_name)


# Регистрцация. Сохранение имени имени
@user_router.message(registration.first_name)
async def first_name_user(message: types.Message, state: FSMContext):
    first_name = message.text.capitalize()
    await state.update_data(first_name=first_name)
    await message.answer('Отправь мне свою фамилию:\n')
    await state.set_state(registration.last_name)


# Регистрцация. Сохранение фамилии ит выбор должности
@user_router.message(registration.last_name)
async def last_name_user(message: types.Message, state: FSMContext):
    last_name = message.text.capitalize()
    await state.update_data(last_name=last_name)

    role_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Начальник сектора', callback_data='position_ns')],
            [InlineKeyboardButton(text='Эксперт', callback_data='position_expert')],
            [InlineKeyboardButton(text='Аналитик', callback_data='position_analyst')]
        ])
    await message.answer('Укажи свою должность', reply_markup=role_markup)
    await state.set_state(registration.role)

@user_router.callback_query(registration.role)
async def choise_role(call: CallbackQuery, bot: Bot, state: FSMContext):
    role = call.data[9:]
    await state.update_data(role=role)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.edit_text(text=f'Вы выбрали: {role_dict[role]}')
    data = await state.get_data()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    sop = data.get('sop')

    finnaly_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Данные корректны', callback_data='finnaly_register')],
            [InlineKeyboardButton(text='Отмена', callback_data='quit')],
        ])


    await bot.send_message(text='Проверь корректность внесенных данных:\n'
                                f'Имя: {first_name}\n'
                                f'Фамилия: {last_name}\n'
                                f'СОП: {sop_dict[sop]}\n'
                                f'Должность: {role_dict[role]}\n', chat_id=call.from_user.id, reply_markup=finnaly_markup)
    await state.set_state(registration.finnaly)



@user_router.callback_query(registration.finnaly)
async def finnaly_registration(call: CallbackQuery, bot: Bot, state: FSMContext):
    if call.data == 'quit':
        await state.clear()
        await call.message.edit_reply_markup(reply_markup=None)
        await bot.send_message(chat_id=call.from_user.id, text="Вы отменили регистрацию ⚠")

    else:
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        sop = data.get('sop')
        role = data.get('role')

        await commands.create_user(
            user_id=call.from_user.id,
            first_name=first_name,
            last_name=last_name,
            access='agreement' if role == 'ns' else 'user',
            role=role,
            status="active",
            photo='null',
            sop=sop
        )

        await bot.send_message(chat_id=call.from_user.id, text=f"Ты успешно зарегистрирован!\n"
                                    "Чтобы воспользоваться мной нажми 'Меню'\n", reply_markup=start_menu)
        await state.clear()



# @send_news_router.callback_query(Text('help'))
# async def return_access(call: types.CallbackQuery):
#     call.message.answer('Если пропадет кнопка меню, отправь команду /start'
#                         '<i>Раздел помощи находится в работе</i>')


    # user = await commands.select_user(user_id=message.from_user.id)
    # if not user or user.status != "active":
    #     await message.answer(text='Для работы с ботом зарегистрируйся по команде /start')
    # else:
    #     if user.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids:
    #         await message.answer(f"Вам доступны следующие команды:\n"
    #                              f"/changerole - позволяет назначать экспертов и аналитиков\n"
    #                              f"/changeaccess - позволяет назначать заместителя для согласований\n"
    #                              f"/my_team - показывает информацию о сотрудниках\n"
    #                              f"/lifehacks - чек лист для исключения #5, #7\n"
    #                              f"/reliz - помощь при отправке релиза по почте")
    #     elif user.access == 'agreement':
    #         await message.answer(f'Вам доступны следующие команды:\n'
    #                              f"/changeacces - позволяет назначать нового заместителя для согласований или вернуть согласование НС\n"
    #                              f"lifehacks - чек лист для исключения #5, #7\n"
    #                              f"/reliz - помощь при отправке релиза по почте")
    #     else:
    #         await message.answer(f"Вам доступны следующие команды:\n"
    #                              f"/news - позволяет отправлять новость на согласование\n"
    #                              f"/lifehacks - чек лист для исключения #5, #7\n"
    #                              f"/reliz - помощь при отправке релиза по почте")
    #


