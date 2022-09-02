from emoji import emojize
from sqlalchemy import String, Column, Integer
from sqlalchemy.orm import relationship
from bot import app
from bot.models.extensions.language.trigger_word import TriggerWord
from db.model import Model


class Trigger(app.base, Model):
    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    positive_emoji_code = Column(String(255), nullable=False)
    negative_emoji_code = Column(String(255), nullable=False)
    trigger_words = relationship("TriggerWord")

    @property
    def words(self):
        for trigger_word in self.trigger_words:
            yield trigger_word.word

    @property
    def positive_emoji(self):
        return emojize(self.positive_emoji_code, use_aliases=True)

    @property
    def negative_emoji(self):
        return emojize(self.negative_emoji_code, use_aliases=True)

    def add_trigger_word(self, trigger_word):
        TriggerWord(trigger_id=self.id, word=trigger_word).save()

    def remove_trigger_word(self, trigger_word):
        TriggerWord.where(trigger_id=self.id, word=trigger_word).first().delete()
