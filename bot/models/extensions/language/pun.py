from sqlalchemy import Text, Column, Integer
from sqlalchemy.orm import relationship
from bot import app
from db.model import Model


class Pun(app.base, Model):
    __tablename__ = 'puns'

    id = Column(Integer, primary_key=True)
    text = Column(Text(), unique=True)
    pun_words = relationship("PunWord")

    @property
    def words(self):
        for pun_word in self.pun_words:
            yield pun_word.word
