import aiofiles
from aiocsv import AsyncDictWriter
from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
from loader import config
from tgbot.keyboards.news_callback import ChangeRoleCB, ChangeAccessCB, DeleteUserCB
from tgbot.models import db_commands as commands
import os

# from tgbot.filters.admin import AdminFilter

admin_router = Router()
# admin_router.message.filter(AdminFilter())
roles = {'team_leader': 'Начальник сектора', 'expert': 'Эксперт', 'analyst': 'Аналитик'}


@admin_router.message(commands=["changerole"])
async def chose_role(message: Message):
    user = await commands.select_user(user_id=message.from_user.id)
    if user.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids:
        if user.role == 'team_leader':
            keyboard = InlineKeyboardMarkup(row_width=2,
                                            inline_keyboard=[
                                                [
                                                    InlineKeyboardButton(text='Эксперт', callback_data='cr_to_expert'),
                                                    InlineKeyboardButton(text='Аналитик', callback_data='cr_to_analyst')
                                                ],
                                                [
                                                    InlineKeyboardButton(text='Отменить', callback_data='quit')
                                                ]
                                            ])
            await message.answer(text="Кем назначаем?", reply_markup=keyboard)
        elif message.from_user.id in config.tg_bot.admin_ids:
            keyboard = InlineKeyboardMarkup(row_width=3,
                                            inline_keyboard=[
                                                [
                                                    InlineKeyboardButton(text='НС', callback_data='cr_to_team_leader'),
                                                    InlineKeyboardButton(text='Эксперт', callback_data='cr_to_expert'),
                                                    InlineKeyboardButton(text='Аналитик', callback_data='cr_to_analyst')
                                                ],
                                                [
                                                    InlineKeyboardButton(text='Отменить', callback_data='quit')
                                                ]
                                            ])
            await message.answer(text="Кем назначаем?", reply_markup=keyboard)
    else:
        await message.answer(f"Вы не являетесь начальником сектора или администратором")


@admin_router.callback_query(text='quit')
async def quit(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили назначение роли ⚠", reply_markup=None)


@admin_router.callback_query(text_contains='cr_to_')
async def change_user(call: CallbackQuery, bot: Bot):
    new_role = call.data[6:]
    changer = await commands.select_user(user_id=call.from_user.id)
    users = await commands.select_all_users()
    if changer.role == 'team_leader':
        keyboard = InlineKeyboardBuilder()
        for user in users:
            # пропускает текущего пользователя
            if call.from_user.id == user.user_id:
                continue
            # пропускает текущего пользователя у которого уже присвоена новая роль
            if user.role == new_role:
                continue
            user = InlineKeyboardButton(text=f'{user.last_name} {user.first_name[0]}.',
                                        callback_data=ChangeRoleCB(user_id=user.user_id, new_role=new_role).pack())
            keyboard.row(user)
        quit_button = InlineKeyboardButton(text='Отменить', callback_data='quit')
        keyboard.adjust(3)
        keyboard.row(quit_button)
        await call.message.edit_text(text="Выберите сотрудника для присвоения роли", reply_markup=keyboard.as_markup())


    elif call.from_user.id in config.tg_bot.admin_ids:
        keyboard = InlineKeyboardBuilder()
        for user in users:
            # пропускает текущего пользователя
            # if call.from_user.id == user.user_id:
            #     continue
            if user.role == new_role:
                continue
            user = InlineKeyboardButton(text=f'{user.last_name} {user.first_name[0]}.',
                                        callback_data=ChangeRoleCB(user_id=user.user_id, new_role=new_role).pack())
            keyboard.add(user)
        quit_button = InlineKeyboardButton(text='Отменить', callback_data='quit')
        keyboard.adjust(3)
        keyboard.row(quit_button)
        await call.message.edit_text(text="Выберите сотрудника для присвоения роли", reply_markup=keyboard.as_markup())


@admin_router.callback_query(ChangeRoleCB.filter())
async def change_role(call: CallbackQuery, callback_data: ChangeRoleCB):
    await call.answer(cache_time=60)

    user_id = callback_data.user_id
    new_role = callback_data.new_role
    user = await commands.select_user(user_id)
    await commands.update_role(user_id=user_id, role=new_role)
    await call.message.edit_text(
        text=f'К сотруднику {user.first_name} {user.last_name} применена роль {roles[new_role]}')


@admin_router.message(commands=["my_team"])
async def my_team(message: Message):
    user = await commands.select_user(user_id=message.from_user.id)
    if user.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids:
        text = ""
        users = await commands.select_all_users()
        for user in users:
            text_new = (
                f"{user.last_name} {user.first_name}. Роль {roles[user.role]}. Бонусы/Ошибки: {user.bonus}/{user.mistake}\n")
            text += text_new
        await message.answer(text=text)
    else:
        await message.answer(f"Вы не являетесь начальником сектора или администратором")


@admin_router.message(commands=["my_team_export"])
async def my_team_export(message: Message):
    team_leader = await commands.select_user(user_id=message.from_user.id)
    if team_leader.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids:
        await message.answer('CSV файл загружается...')
        users = await commands.select_all_users()
        filename = f'logs/my_team.csv'

        async with aiofiles.open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = AsyncDictWriter(file, ['user_id', 'tg_first_name', 'username', 'first_name', 'last_name',
                                            'access', 'role', 'bonus', 'mistake', 'status', 'is_active'])
            await writer.writeheader()
            for user in users:
                row = {
                    'user_id': user.user_id,
                    'tg_first_name': user.tg_first_name,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'access': user.access,
                    'role': user.role,
                    'bonus': user.bonus,
                    'mistake': user.mistake,
                    'status': user.status,
                    'is_active': user.is_active
                }
                await writer.writerow(row)

        time.sleep(3)
        file = FSInputFile('logs/my_team.csv')
        await message.answer_document(document=file)

        time.sleep(3)
        os.remove('logs/my_team.csv')
    else:
        await message.answer(f"Вы не являетесь начальником сектора или администратором")


@admin_router.message(commands=["changeaccess"])
async def changeaccess(message: Message):
    user = await commands.select_user(user_id=message.from_user.id)
    if user.role == 'team_leader' or message.from_user.id in config.tg_bot.admin_ids or user.access == 'SuperUser':
        keyboard = InlineKeyboardMarkup(row_width=2,
                                        inline_keyboard=[
                                            [
                                                InlineKeyboardButton(text='Назначить заместителя',
                                                                     callback_data='ca_to_new'),
                                                InlineKeyboardButton(text='Вернуть согласование НС',
                                                                     callback_data='ca_to_return')
                                            ],
                                            [
                                                InlineKeyboardButton(text='Отменить', callback_data='quit_ca')
                                            ]
                                        ])

        await message.answer(text="Выбери необходимый вариант", reply_markup=keyboard)
    else:

        await message.answer(f"Вы не являетесь начальником сектора, заместителем или администратором")


@admin_router.callback_query(text='ca_to_new')
async def change_access_new(call: CallbackQuery):
    changer = await commands.select_user(user_id=call.from_user.id)
    users = await commands.select_all_users()
    keyboard = InlineKeyboardBuilder()
    for user in users:
        # пропускает текущего пользователя
        if call.from_user.id == user.user_id:
            continue
        if user.role != 'expert':
            continue
        user = InlineKeyboardButton(text=f'{user.last_name} {user.first_name[0]}.',
                                    callback_data=ChangeAccessCB(user_id=user.user_id).pack())
        keyboard.row(user)
    quit_button = InlineKeyboardButton(text='Отменить', callback_data='quit_ca')
    keyboard.adjust(2)
    keyboard.row(quit_button)
    await call.message.edit_text(text="Выберите сотрудника для присвоения роли", reply_markup=keyboard.as_markup())


@admin_router.callback_query(text='quit_ca')
async def quit_ca(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили назначение заместителя ⚠", reply_markup=None)


@admin_router.callback_query(ChangeAccessCB.filter())
async def change_role(call: CallbackQuery, callback_data: ChangeAccessCB):
    await call.answer(cache_time=60)
    user_id = callback_data.user_id
    new_access = "SuperUser"
    users = await commands.select_all_users()
    for user in users:
        await commands.update_access(user_id=user.user_id, access="user")
    user = await commands.select_user(user_id)
    await commands.update_access(user_id=user_id, access=new_access)
    await call.message.edit_text(
        text=f'Сотрудник {user.first_name} {user.last_name} назначен заместителем')


@admin_router.callback_query(text='ca_to_return')
async def return_access(call: CallbackQuery):
    await call.answer(cache_time=60)
    new_access = "SuperUser"
    users = await commands.select_all_users()
    for user in users:
        await commands.update_access(user_id=user.user_id, access="user")
    user = await commands.select_user_by_role("team_leader")
    await commands.update_access(user_id=user.user_id, access=new_access)
    await call.message.edit_text(
        text=f'Права согласования возвращены НС {user.first_name} {user.last_name}')


#
@admin_router.message(commands=["delete"])
async def delete(message: Message):

    if message.from_user.id in config.tg_bot.admin_ids:
        users = await commands.select_all_users()
        keyboard = InlineKeyboardBuilder()
        for user in users:
            user = InlineKeyboardButton(text=f'{user.last_name} {user.first_name[0]}.',
                                        callback_data=DeleteUserCB(user_id=user.user_id).pack())
            keyboard.row(user)
        quit_button = InlineKeyboardButton(text='Отменить', callback_data='delete_stop')
        keyboard.adjust(4)
        keyboard.row(quit_button)
        await message.answer(text="Выберите сотрудника для удаления", reply_markup=keyboard.as_markup())
    else:
        await message.answer(f"Вы не являетесь администратором")


@admin_router.callback_query(text='delete_stop')
async def delete_stop(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили удаление пользователя ⚠", reply_markup=None)


@admin_router.callback_query(DeleteUserCB.filter())
async def delete_user_cb(call: CallbackQuery, callback_data: DeleteUserCB):
    await call.answer(cache_time=60)
    user_id = callback_data.user_id
    print(user_id)
    user = await commands.select_user(user_id=user_id)
    await commands.delete_user(user_id)
    await call.message.edit_text(
        text=f'Сотрудник {user.first_name} {user.last_name} удален')
