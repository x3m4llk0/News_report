from sqlalchemy import BigInteger, Column, String, sql
from tgbot.models.db_gino import TimeBaseModel
from gino import Gino

db = Gino()


class User(TimeBaseModel):
    __tablename__ = 'users'
    #создание таблицы "users" в sql. Ниже параметры для заполнения таблицы
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(200))
    username = Column(String(200))
    first_name = Column(String(200))
    last_name = Column(String(200))
    access = Column(String(30))
    role = Column(String(30))
    bonus = Column(BigInteger)
    mistake = Column(BigInteger)
    status = Column(String(25))
    is_active = Column(db.Boolean, default=False)

    query: sql.select

