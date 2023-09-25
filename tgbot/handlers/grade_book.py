from aiogram import Router, Bot, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
from loader import config
from tgbot.keyboards.grade_book_callback import SendLike, SendMistake, SendBonusMistake, UpdateBonusMistake
from tgbot.misc.states import send_bonus, add_comment
from tgbot.models import db_commands as commands
import os
from aiogram.filters.command import Command
from aiogram import F
# from tgbot.filters.admin import AdminFilter

grade_book_router = Router()

def check_quarter():
    import datetime
    import math
    now_date = datetime.datetime.now()
    quarter = math.ceil(now_date.month/3.)
    return quarter

@grade_book_router.callback_query(Text('grade_book'))
async def main_menu(call: CallbackQuery, bot: Bot):
    await call.answer(cache_time=1)
    keyboard = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Бонус', callback_data='grade_book_bonus')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Ошибку', callback_data='grade_book_mistake')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Лайк', callback_data='like')
                                        ],
                                        [
                                            InlineKeyboardButton(text='Отмена', callback_data='quit_gb')
                                        ]
                                    ])
    await call.message.edit_text(text="Dashboard: https://sop-dashboard.ru \nЧто вы желаете внести?", reply_markup=keyboard)


@grade_book_router.callback_query(Text(text='quit_gb'))
async def quit_cr(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text="Вы отменили операцию ⚠", reply_markup=None)


"""
функция установки лайка
"""
@grade_book_router.callback_query(Text(text='like'))
async def users_for_like(call: CallbackQuery):
    initiator = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(initiator.sop)
    keyboard = InlineKeyboardBuilder()
    for user_id in sop_dict:
        # пропускает текущего пользователя
        user = await commands.select_user(user_id)

        if call.from_user.id == user.user_id:
            continue
        user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                    callback_data=SendLike(employee=user.user_id).pack())
        keyboard.row(user)
        quit_button = InlineKeyboardButton(text='Отмена', callback_data='quit_cr')
        keyboard.adjust(3)
    keyboard.row(quit_button)
    await call.message.edit_text(text="Выберите сотрудника", reply_markup=keyboard.as_markup())


@grade_book_router.callback_query(SendLike.filter())
async def send_like(call: CallbackQuery, callback_data: SendLike, bot: Bot):
    await call.answer(cache_time=1)
    employee = callback_data.employee
    initiator = call.from_user.id
    employee_id = await commands.select_user(employee)
    initiator_id = await commands.select_user(initiator)
    id = await commands.create_like(employee=employee, initiator=initiator, quarter=check_quarter())
    await call.message.edit_text(text=f"Лайк поставлен сотруднику: {employee_id.last_name} {employee_id.first_name[0]}.", reply_markup=None)
    await bot.send_message(chat_id=employee, text=f'Сотрудник {initiator_id.last_name} {initiator_id.first_name[0]}. поставил тебе лайкос.')
"""
функция установки лайка конец
"""

criterion_dict = {1: 'Ответственность', 2: 'Готовность к изменениям', 3: 'Саморазвитие и развитие команды',
                 4: 'Открытость', 5: 'Командное взаимодействие', 6: 'Качество услуг', 7: 'Удовлетворение потребностей'}

bonus_mistake = {'bonus': 'Бонус', 'mistake': 'Ошибка'}


@grade_book_router.callback_query(Text(contains='grade_book_'))
async def users_for_bonus(call: CallbackQuery):
    initiator = await commands.select_user(call.from_user.id)
    sop_dict = await commands.all_users_by_sop(initiator.sop)
    gb_type = call.data[11:]
    keyboard = InlineKeyboardBuilder()
    for user_id in sop_dict:
        # пропускает текущего пользователя
        user = await commands.select_user(user_id)
        user = InlineKeyboardButton(text=f'👤{user.last_name} {user.first_name[0]}.',
                                    callback_data=SendBonusMistake(employee=user.user_id, gb_type=gb_type).pack())
        keyboard.row(user)
        quit_button = InlineKeyboardButton(text='Отмена', callback_data='quit_gb')
        keyboard.adjust(3)
    keyboard.row(quit_button)
    await call.message.edit_text(text="Выберите сотрудника", reply_markup=keyboard.as_markup())


@grade_book_router.callback_query(SendBonusMistake.filter())
async def add_activity(call: CallbackQuery, callback_data: SendBonusMistake, state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text('Опиши активность', reply_markup=None)
    await state.update_data(employee_id=callback_data.employee, gb_type=callback_data.gb_type)
    await state.set_state(send_bonus.activity)


@grade_book_router.message(send_bonus.activity)
async def add_criterion(message: types.Message, state: FSMContext, bot: Bot):
    activity = message.text
    await state.update_data(activity=message.text)
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text=criterion_dict[1], callback_data='criterion_1')
    button_2 = InlineKeyboardButton(text=criterion_dict[2], callback_data='criterion_2')
    button_3 = InlineKeyboardButton(text=criterion_dict[3], callback_data='criterion_3')
    button_4 = InlineKeyboardButton(text=criterion_dict[4], callback_data='criterion_4')
    button_5 = InlineKeyboardButton(text=criterion_dict[5], callback_data='criterion_5')
    button_6 = InlineKeyboardButton(text=criterion_dict[6], callback_data='criterion_6')
    button_7 = InlineKeyboardButton(text=criterion_dict[7], callback_data='criterion_7')
    button_8 = InlineKeyboardButton(text='Отменить', callback_data='quit_gb')
    keyboard.add(button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8)
    keyboard.adjust(1)
    await message.answer(text='Выбери критерий', reply_markup=keyboard.as_markup())
    await state.set_state(send_bonus.criterion)

@grade_book_router.callback_query(send_bonus.criterion)
async def add_quarter(call: CallbackQuery, state: FSMContext):
    await state.update_data(criterion=criterion_dict[int(call.data[10:])])
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='1Q', callback_data='quarter_1')
    button_2 = InlineKeyboardButton(text='2Q', callback_data='quarter_2')
    button_3 = InlineKeyboardButton(text='3Q', callback_data='quarter_3')
    button_4 = InlineKeyboardButton(text='4Q', callback_data='quarter_4')
    button_5 = InlineKeyboardButton(text='Отменить', callback_data='quit_gb')
    keyboard.row(button_1,button_2)
    keyboard.row(button_3,button_4)
    keyboard.row(button_5)
    await call.message.edit_text(text='Выберите квартал', reply_markup=keyboard.as_markup())
    await state.set_state(send_bonus.quarter)

@grade_book_router.callback_query(send_bonus.quarter)
async def confirmation(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(quarter=call.data[8:])
    data = await state.get_data()
    employee_id = data.get('employee_id')
    employee = await commands.select_user(employee_id)
    quarter = data.get('quarter')
    criterion = data.get('criterion')
    activity = data.get('activity')
    gb_type = data.get('gb_type')
    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Подтверждаю', callback_data='complite')
    button_2 = InlineKeyboardButton(text='Отменить', callback_data='quit_gb')
    keyboard.add(button_1, button_2)

    await call.message.edit_text(text=f'Вы вносите {bonus_mistake[gb_type]}/у\n'
                                   f'Получатель: {employee.last_name} {employee.first_name[0]}. \n'
                                   f'Кватал: {quarter}\n'
                                   f'Критерий: {criterion}\n'
                                   f'Активность: {activity}', reply_markup=keyboard.as_markup())
    await state.set_state(send_bonus.confirmation)


@grade_book_router.callback_query(send_bonus.confirmation)
async def create_bonus_mistake(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.delete()
    data = await state.get_data()
    employee = data.get('employee_id')
    quarter = int(data.get('quarter'))
    criterion = data.get('criterion')
    activity = data.get('activity')
    gb_type = data.get('gb_type')
    initiator = call.from_user.id
    if gb_type == 'bonus':
        id = await commands.create_bonus(initiator=initiator, employee=employee, quarter=quarter, activity=activity,
                      comment='', criterion=criterion)
    elif gb_type == 'mistake':
        id = await commands.create_mistake(initiator=initiator, employee=employee, quarter=quarter, activity=activity,
                      comment='Требует заполнения', criterion=criterion)

    await state.clear()

    keyboard = InlineKeyboardBuilder()
    button_1 = InlineKeyboardButton(text='Добавить комментарий',  callback_data=UpdateBonusMistake(id=id, gb_type=gb_type, comment='add_comment').pack())
    button_2 = InlineKeyboardButton(text='Оставить без комментариев', callback_data=UpdateBonusMistake(id=id, gb_type=gb_type, comment='no_comment').pack())
    keyboard.row(button_1, button_2)


    initiator = await commands.select_user(call.from_user.id)
    employee = await commands.select_user(employee)
    ns_user_id = await commands.all_users_by_sop_and_role(initiator.sop, 'ns')
    #сообщаем получателю и НСу
    if initiator.user_id != employee.user_id:
        await call.message.answer(f'{bonus_mistake[gb_type]} внесен/а')
        await bot.send_message(chat_id=employee.user_id, text=f'Сотрудник {initiator.last_name} {initiator.first_name[0]}. внес тебе {bonus_mistake[gb_type]}/у:\n'
                                                              f'{activity}.', reply_markup=keyboard.as_markup())
        await bot.send_message(chat_id=ns_user_id[0], text=f'Сотрудник {initiator.last_name} {initiator.first_name[0]}. внес {bonus_mistake[gb_type]}/у {employee.last_name} {employee.first_name[0]}:\n'
                                                           f'{activity}.')
    #сообщаем себе и НСу
    elif initiator.user_id == employee.user_id:
            await call.message.answer(text=f'{bonus_mistake[gb_type]} внесен/а', reply_markup=keyboard.as_markup())
            await bot.send_message(chat_id=ns_user_id[0], text=f'Сотрудник {initiator.last_name} {initiator.first_name[0]}. внес себе {bonus_mistake[gb_type]}/у:\n'
                                                               f'{activity}')

@grade_book_router.callback_query(UpdateBonusMistake.filter())
async def choise_comment(call: CallbackQuery, callback_data: UpdateBonusMistake, state: FSMContext):
    await state.update_data(id=callback_data.id, gb_type= callback_data.gb_type)

    if callback_data.gb_type == 'bonus':
        if callback_data.comment == 'add_comment':
            await call.message.edit_text(text='Напиши свой комментарий', reply_markup=None)
            await state.set_state(add_comment.add_comment)
        elif callback_data.comment == 'no_comment':
            await commands.update_comment_bonus(id=callback_data.id, comment=' ')
            await call.message.edit_text(text='Без комментариев', reply_markup=None)


    elif callback_data.gb_type == 'mistake':
        if callback_data.comment == 'add_comment':
            await call.message.edit_text(text='Напиши свой комментарий', reply_markup=None)
            await state.set_state(add_comment.add_comment)
        elif callback_data.comment == 'no_comment':
            await commands.update_comment_mistake(id=callback_data.id, comment='Без комментариев')
            await call.message.edit_text(text='Без комментариев',reply_markup=None)


@grade_book_router.message(add_comment.add_comment)
async def add_comments(message: types.Message, state: FSMContext):
    data = await state.get_data()
    gb_type = data.get('gb_type')
    id = data.get('id')

    if gb_type == 'bonus':
        await commands.update_comment_bonus(id=id, comment=message.text)

    elif gb_type == 'mistake':
        await commands.update_comment_mistake(id=id, comment=message.text)

    await message.answer('Комментарий внесен')