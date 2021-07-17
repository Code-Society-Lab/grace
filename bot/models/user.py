from sqlalchemy import Column, Integer, String

from bot.models import BASE


class User(BASE):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)