from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import relationship

from bot import app
from db.model import Model


class Bot(app.base, Model):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    prefix = Column(String, nullable=False)
    description = Column(String)
    default_color_code = Column(String)

    welcome_message = Column(String)
    channels = relationship("BotChannel", cascade="all")
