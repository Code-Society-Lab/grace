from sqlalchemy import String, Column, ForeignKey
from sqlalchemy.orm import relationship
from bot import app
from db.model import Model


class PunWord(app.base, Model):
    __tablename__ = 'pun_words'

    pun_id = Column(ForeignKey("puns.id"), primary_key=True)
    word = Column(String(255), primary_key=True)
