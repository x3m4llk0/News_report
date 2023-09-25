from tgbot.models.db_gino import Sessions
from tgbot.models.schemas.models import User, Quarter, Like, Bonus, Mistake
from asyncpg import UniqueViolationError


# Быстрые команда Регистрации Пользователей
# Передача данных в таблицы БД
# async def create_user(user_id: int, first_name: str, last_name: str, access: str,
#                       role: str, status: str, photo: None, sop: str):
#     try:
#         user = User(user_id=user_id, first_name=first_name, last_name=last_name, access=access, role=role,
#                     status=status, photo=None, sop=sop)
#         await user.create()
#     except UniqueViolationError:
#         print('Пользователь не добавлен, так как уже зарегистрирован.')



# Функция которая выбирает всех пользователей
async def select_all_users():
    users = await User.query.gino.all()
    return users


# Функция которая выбирает по статусу Актив
async def select_registration():
    registration = await User.query.where(User.status == 'active').gino.first()
    return registration


# Функция которая выбирает Пользователя
async def select_user(user_id):
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


# Функция удаления пользователя
# async def delete_user(user_id: int):
#     await User.delete.where(User.user_id == user_id).gino.status()


async def select_user_by_role(role: str):
    user = await User.query.where(User.role == role).gino.first()
    return user



# Список пользователей по доступу
async def user_rights_access():
    users_access = await User.query.where(User.access == 'agreement').gino.all()
    return users_access


# Сотрировка пользователей по должности
async def all_users_by_role(role) -> list:
    users_id = []
    users_role = await User.query.where(User.role == role).gino.all()
    for user in users_role:
        users_id.append(user.user_id)
    return users_id


# Сотрировка пользователей по доступу
async def all_users_by_access(access) -> list:
    users_id = []
    users_access = await User.query.where(User.access == access).gino.all()
    for user in users_access:
        users_id.append(user.user_id)
    return users_id

# Сотрировка пользователей по сопу
async def all_users_by_sop(sop) -> list:
    users_id = []
    users_sop = await User.query.where(User.sop == sop).gino.all()
    for user in users_sop:
        users_id.append(user.user_id)
    return users_id

# Функция которая сортирует по сопу и должности, возвращает список айди
async def all_users_by_sop_and_role(sop, role) -> list:
    users_id =[]
    users = await User.query.where(User.sop == sop).gino.all()
    # print(users)
    for user in users:
        if user.role == role:
            users_id.append(user.user_id)
            # print(user)
    return users_id

# Функция которая сортирует по сопу и должности, возвращает список айди
async def all_users_by_sop_and_agreement(sop) -> list:
    users_id =[]
    users = await User.query.where(User.sop == sop).gino.all()
    # print(users)
    for user in users:
        if user.access == 'agreement':
            users_id.append(user.user_id)
            # print(user)
    return users_id


# Функция которая обновляет доступ Пользователя
async def update_access(user_id, access):
    user = await select_user(user_id)
    await user.update(access=access).apply()


# Функция которая обновляет роль Пользователя
async def update_role(user_id, role):
    user = await select_user(user_id)
    await user.update(role=role).apply()


# Функция которая обновляет бонусы Пользователя
async def update_bonus(user_id, bonus):
    user = await select_user(user_id)
    await user.update(bonus=bonus).apply()


# Функция которая обновляет ошибки Пользователя
async def update_mistake(user_id, mistake):
    user = await select_user(user_id)
    await user.update(mistake=mistake).apply()


async def get_session(user_id):
    return await Sessions.query.where(Sessions.user_id == user_id).gino.first()


async def create_session(user_id):
    session = Sessions(user_id=user_id)
    await session.create()


async def select_all_quarter():
    users = await Quarter.query.gino.all()
    return users

#создание лайка
async def create_like(initiator: int, employee: int, quarter: int):
    like = Like(initiator_id=initiator, employee_id=employee, quarter_id=quarter)
    await like.create()
    return like.id


# создание бонуса
async def create_bonus(initiator: int, employee: int, quarter: int, activity: str,
                      comment: str, criterion: str):
    bonus = Bonus(initiator_id=initiator, employee_id=employee, quarter_id=quarter, activity=activity,
                  comment=comment, criterion=criterion)
    await bonus.create()
    return bonus.id

# создание ошибки
async def create_mistake(initiator: int, employee: int, quarter: int, activity: str,
                      comment: str, criterion: str):
    mistake = Mistake(initiator_id=initiator, employee_id=employee, quarter_id=quarter, activity=activity,
                  comment=comment, criterion=criterion)
    await mistake.create()
    return mistake.id


# Функция которая выбирает бонус
async def select_bonus(id):
    user = await Bonus.query.where(Bonus.id == id).gino.first()
    return user

# Функция которая обновляет бонус
async def update_comment_bonus(id, comment):
    bonus = await select_bonus(id)
    await bonus.update(comment=comment).apply()

# Функция которая выбирает ошибку
async def select_mistake(id):
    user = await Mistake.query.where(Mistake.id == id).gino.first()
    return user

# Функция которая обновляет бонус
async def update_comment_mistake(id, comment):
    mistake = await select_mistake(id)
    await mistake.update(comment=comment).apply()