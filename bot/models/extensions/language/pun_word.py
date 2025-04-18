from emoji import emojize
from sqlalchemy import Integer, String, Column, ForeignKey
from grace.model import Model
from bot import app


class PunWord(app.base, Model):
    __tablename__ = 'pun_words'

    id  = Column(Integer, primary_key=True)
    pun_id = Column(ForeignKey("puns.id"))
    word = Column(String(255), nullable=False)
    emoji_code = Column(String(255))

    def emoji(self):
        return emojize(self.emoji_code, language='alias')