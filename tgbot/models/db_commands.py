from tgbot.models.db_gino import Sessions
from tgbot.models.schemas.user import User
from asyncpg import UniqueViolationError


# Быстрые команда Регистрации Пользователей
# Передача данных в таблицы БД
async def create_user(user_id: int, tg_first_name: str, username: str, first_name: str, last_name: str, access: str,
                   role: str, bonus: int, mistake: int, status: str, is_active: bool):
    try:
        user = User(user_id=user_id, tg_first_name=tg_first_name, username=username,
                    first_name=first_name, last_name=last_name, access=access, role=role,
                    bonus=bonus, mistake=mistake, status=status, is_active=is_active)
        await user.create()
    except UniqueViolationError:
        print('Пользователь не добавлен, так как уже зарегистрирован.')



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


# Функция которая выбирает Пользователя
async def select_user_role(role):
    user = await User.query.where(User.role == role).gino.first()
    return user


# Функция удаления пользователя
async def delete_user(user_id: int):
    await User.delete.where(User.user_id == user_id).gino.status()


# Функция которая выбирает по User_Id
async def select_registration_by_user_id(user_id: int):
    registration = await User.query.where(User.user_id == user_id).gino.first()
    return registration


# Функция которая выбирает по имени Пользователя
async def select_registration_by_first_name(first_name: str):
    registration = await User.query.where(User.first_name == first_name).gino.first()
    return registration


# Функция которая выбирает по Фамилии Пользователя
async def select_registration_by_last_name(last_name: str):
    registration = await User.query.where(User.last_name == last_name).gino.first()
    return registration


async def select_user_by_role(role: str):
    registration = await User.query.where(User.role == role).gino.first()
    return registration

# Список пользователей по доступу
async def user_rights_access():
    users_access = await User.query.where(User.access == 'SuperUser').gino.all()
    return users_access


async def user_rights_role():
    users_access = await User.query.where(User.role == 'team_leader').gino.all()
    return users_access


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
