from sqlalchemy import String, Column, ForeignKey
from grace.model import Model
from bot import app


class TriggerWord(app.base, Model):
    __tablename__ = 'trigger_words'

    trigger_id = Column(ForeignKey('triggers.id'), primary_key=True)
    word = Column(String(255), primary_key=True)
