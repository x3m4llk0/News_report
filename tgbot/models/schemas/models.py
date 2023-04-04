from sqlalchemy import BigInteger, Column, String, sql, Integer, ForeignKey
from tgbot.models.db_gino import TimeBaseModel, BaseModel
from gino import Gino

db = Gino()


class User(TimeBaseModel):
    __tablename__ = 'db_api_user'
    #создание таблицы "users" в sql. Ниже параметры для заполнения таблицы
    # user_id = Column(BigInteger, primary_key=True)
    # tg_first_name = Column(String(200))
    # username = Column(String(200))
    # first_name = Column(String(200))
    # last_name = Column(String(200))
    # access = Column(String(30))
    # role = Column(String(30))
    # bonus = Column(BigInteger)
    # mistake = Column(BigInteger)
    # status = Column(String(25))
    # is_active = Column(db.Boolean, default=False)

    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    access = Column(String(100))
    role = Column(String(100))
    status = Column(String(100))
    photo = Column(String(150), nullable=True)
    sop = Column(String(100))
    query: sql.select

#
class Quarter(TimeBaseModel):
    __tablename__ = "db_api_quarter"
    id = Column(BigInteger, primary_key=True)
    quarter = Column(Integer)
    year = Column(Integer)
    query: sql.select


class  Bonus(TimeBaseModel):
    __tablename__ = "db_api_bonus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    initiator = Column(ForeignKey("db_api_user.user_id"))
    employee = Column(ForeignKey("db_api_user.user_id"))
    quarter = Column(ForeignKey("db_api_quarter.id"))
    activity = Column(String(200))
    comment = Column(String(200))
    criterion = Column(String(200))
