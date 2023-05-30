from datetime import timedelta
from sqlalchemy import Text, Column, Integer, DateTime
from sqlalchemy.orm import relationship
from bot import app
from bot.models.extensions.language.pun_word import PunWord
from bot.models.bot import BotSettings
from db.model import Model


class Pun(app.base, Model):
    __tablename__ = "puns"

    id = Column(Integer, primary_key=True)
    text = Column(Text(), unique=True)
    last_invoked = Column(DateTime)
    pun_words = relationship("PunWord", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def words(self):
        for pun_word in self.pun_words:
            yield pun_word.word

    def has_word(self, word):
        return self.pun_words.filter(PunWord.word == word).count() > 0

    def add_pun_word(self, pun_word, emoji_code):
        PunWord(pun_id=self.id, word=pun_word, emoji_code=emoji_code).save()

    def remove_pun_word(self, pun_word):
        PunWord.where(pun_id=self.id, word=pun_word).first().delete()

    def can_invoke_at_time(self, time):
        cooldown_minutes = BotSettings.settings().puns_cooldown
        cooldown = timedelta(minutes=cooldown_minutes)

        if self.last_invoked is None:
            return True
        else:
            return time - self.last_invoked > cooldown

    def save_last_invoked(self, time):
        self.last_invoked = time
        self.save()
