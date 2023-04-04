import aiofiles

from aiogram import Router, Bot
from aiogram.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
from loader import config
from tgbot.keyboards.news_callback import ChangeRoleCB, ChangeAccessCB, DeleteUserCB
from tgbot.models import db_commands as commands
import os
from aiogram.filters.command import Command

# from tgbot.filters.admin import AdminFilter

admin_router = Router()
# admin_router.message.filter(AdminFilter())
roles = {'ns': 'Начальник сектора', 'expert': 'Эксперт', 'analyst': 'Аналитик'}


@admin_router.callback_query(Text('changerole'))
async def chose_role(call: CallbackQuery, bot: Bot):
    await call.answer(cache_time=1)
    keyboard = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Эксперт', callback_data='cr_to_expert'),
                                            InlineKeyboardButton(text='Аналитик', callback_data='cr_to_analyst')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Отменить', callback_data='quit_cr')
                                        ]
                                    ])
    await call.message.edit_text(text="Кем назначаем?", reply_markup=keyboard)




@admin_router.callback_query(Text(text='quit_cr'))
async def quit_cr(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили назначение роли ⚠", reply_markup=None)


@admin_router.callback_query(Text(contains='cr_to_'))
async def change_user(call: CallbackQuery, bot: Bot):
    new_role = call.data[6:]
    changer = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(changer.sop)
    keyboard = InlineKeyboardBuilder()
    if changer is not None and changer.role == 'ns':
        for user_id in sop_dict:
            # пропускает текущего пользователя
            user = await commands.select_user(user_id)

            if call.from_user.id == user.user_id:
                continue
            # пропускает текущего пользователя у которого уже присвоена новая роль
            if user.role == new_role:
                continue
            user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                        callback_data=ChangeRoleCB(user_id=user.user_id, new_role=new_role).pack())
            keyboard.row(user)

    elif call.from_user.id in config.tg_bot.admin_ids:
        for user_id in sop_dict:
            # пропускает текущего пользователя
            # if call.from_user.id == user.user_id:
            #     continue
            user = await commands.select_user(user_id)
            if user.role == new_role:
                continue
            user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                        callback_data=ChangeRoleCB(user_id=user.user_id, new_role=new_role).pack())
            keyboard.add(user)
    quit_button = InlineKeyboardButton(text='Отменить', callback_data='quit_cr')
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



@admin_router.callback_query(Text('my_team'))
async def my_team(call: CallbackQuery, bot: Bot):
    exporter = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(exporter.sop)
    text = ""
    exporter = await commands.select_user(call.from_user.id)
    if exporter.sop == 'stvp':
        for user_id in sop_dict:
            user = await commands.select_user(user_id)
            text_new = (
                f"<a href='tg://user?id={user.user_id}'>{user.last_name} {user.first_name}</a>. Должность: {roles[user.role]}. {'<b>Согласующий</b>'if user.access == 'agreement' else ''} <i>Бонусы/Ошибки: в работе</i>\n")
            text += text_new
        await call.message.edit_text(text=text)
    else:
        for user_id in sop_dict:
            user = await commands.select_user(user_id)
            text_new = (
                f"<a href='tg://user?id={user.user_id}'>{user.last_name} {user.first_name}</a>. Должность: {roles[user.role]}. {'Согласующий'if user.access == 'agreement' else ''}.\n")
            text += text_new
        await call.message.edit_text(text=text)



@admin_router.callback_query(Text('changeaccess'))
async def changeaccess(call: CallbackQuery, bot: Bot):
    await call.answer(cache_time=1)
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
    await call.message.edit_text(text="Выбери необходимый вариант", reply_markup=keyboard)



@admin_router.callback_query(Text('ca_to_new'))
async def change_access_new(call: CallbackQuery):
    changer = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(changer.sop)
    keyboard = InlineKeyboardBuilder()
    for user_id in sop_dict:
        user = await commands.select_user(user_id)
        # пропускает текущего пользователя
        if call.from_user.id == user.user_id:
            continue
        if user.role != 'expert':
            continue
        user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                    callback_data=ChangeAccessCB(user_id=user.user_id).pack())
        keyboard.row(user)

    quit_button = InlineKeyboardButton(text='Отменить', callback_data='quit_ca')
    keyboard.adjust(2)
    keyboard.row(quit_button)
    await call.message.edit_text(text="Выберите сотрудника для замещения", reply_markup=keyboard.as_markup())


@admin_router.callback_query(Text('quit_ca'))
async def quit_ca(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили назначение заместителя ⚠", reply_markup=None)


@admin_router.callback_query(ChangeAccessCB.filter())
async def change_role(call: CallbackQuery, callback_data: ChangeAccessCB):
    await call.answer(cache_time=1)
    user_id = callback_data.user_id
    new_access = "agreement"

    changer = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(changer.sop)
    for user_id in sop_dict:
        await commands.update_access(user_id=user_id, access="user")
    user = await commands.select_user(user_id)
    await commands.update_access(user_id=user_id, access=new_access)
    await call.message.edit_text(
        text=f'Сотрудник {user.first_name} {user.last_name} назначен заместителем')


@admin_router.callback_query(Text('ca_to_return'))
async def return_access(call: CallbackQuery):
    await call.answer(cache_time=1)
    new_access = "agreement"
    changer = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(changer.sop)
    for user_id in sop_dict:
        await commands.update_access(user_id=user_id, access="user")
    ns_user_id = await commands.all_users_by_sop_and_role(changer.sop, 'ns')
    ns_user = await commands.select_user(ns_user_id[0])
    await commands.update_access(user_id=ns_user.user_id, access=new_access)
    await call.message.edit_text(
        text=f'Права согласования возвращены НС {ns_user.first_name} {ns_user.last_name}')


#
@admin_router.message(Command("delete"))
async def delete(message: Message):
    if message.from_user.id in config.tg_bot.admin_ids:
        users = await commands.select_all_users()
        keyboard = InlineKeyboardBuilder()
        for user in users:
            user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                        callback_data=DeleteUserCB(user_id=user.user_id).pack())
            keyboard.row(user)
        quit_button = InlineKeyboardButton(text='Отменить', callback_data='delete_stop')
        keyboard.adjust(3)
        keyboard.row(quit_button)
        await message.answer(text="Выберите сотрудника для удаления", reply_markup=keyboard.as_markup())
    else:
        await message.answer(f"Вы не являетесь администратором")


@admin_router.callback_query(Text("delete_stop"))
async def delete_stop(call: CallbackQuery, bot: Bot):
    await call.message.edit_text(text="Вы отменили удаление пользователя ⚠", reply_markup=None)


@admin_router.callback_query(DeleteUserCB.filter())
async def delete_user_cb(call: CallbackQuery, callback_data: DeleteUserCB):
    await call.answer(cache_time=1)
    user_id = callback_data.user_id
    print(user_id)
    user = await commands.select_user(user_id=user_id)
    await commands.delete_user(user_id)
    await call.message.edit_text(
        text=f'Сотрудник {user.first_name} {user.last_name} удален')



@admin_router.callback_query(Text('help'))
async def help(call: CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.answer('Если пропадет кнопка меню, отправь команду /start\n'
                        '<i>*Раздел помощи находится в работе*</i>')



# До лучших времен
# @admin_router.message(Command("my_team_export"))
# async def my_team_export(message: Message):
#     changer = await commands.select_user(user_id=message.from_user.id)
#     if changer is not None and changer.role == 'ns' or message.from_user.id in config.tg_bot.admin_ids:
#         await message.answer('CSV файл загружается...')
#         users = await commands.select_all_users()
#         filename = f'logs/my_team.csv'
#
#         async with aiofiles.open(filename, mode='w', encoding='utf-8', newline='') as file:
#             writer = AsyncDictWriter(file, ['user_id', 'tg_first_name', 'username', 'first_name', 'last_name',
#                                             'access', 'role', 'bonus', 'mistake', 'status', 'is_active'])
#             await writer.writeheader()
#             for user in users:
#                 row = {
#                     'user_id': user.user_id,
#                     'tg_first_name': user.tg_first_name,
#                     'username': user.username,
#                     'first_name': user.first_name,
#                     'last_name': user.last_name,
#                     'access': user.access,
#                     'role': user.role,
#                     'bonus': user.bonus,
#                     'mistake': user.mistake,
#                     'status': user.status,
#                     'is_active': user.is_active
#                 }
#                 await writer.writerow(row)
#
#         time.sleep(3)
#         file = FSInputFile('logs/my_team.csv')
#         await message.answer_document(document=file)
#
#         time.sleep(3)
#         os.remove('logs/my_team.csv')
#     else:
#         await message.answer(f"Вы не являетесь начальником сектора или администратором")