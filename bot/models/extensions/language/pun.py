from sqlalchemy import Text, Column, Integer
from sqlalchemy.orm import relationship
from bot import app
from bot.models.extensions.language.pun_word import PunWord
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

    def add_pun_word(self, pun_word, emoji_code):
        PunWord(pun_id=self.id, word=pun_word, emoji_code=emoji_code).save()

    def remove_pun_word(self, pun_word):
        PunWord.where(pun_id=self.id, word=pun_word).first().delete()
