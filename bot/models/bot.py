from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import relationship

from bot import app
from db.model import Model


class Bot(app.base, Model):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    prefix = Column(String(255), nullable=False)
    description = Column(String(255))
    default_color_code = Column(String(255))

    welcome_message = Column(String(255))
    channels = relationship("BotChannel", cascade="all")
