from datetime import datetime, timedelta
from typing import List

from bot.models.bot import BotSettings
from bot.models.extensions.language.pun_word import PunWord
from grace.model import Field, Model, Relationship


class Pun(Model):
    __tablename__ = "puns"

    id: int | None = Field(default=None, primary_key=True)
    text: str | None = Field(unique=True)
    last_invoked: datetime | None = Field(default=None)
    pun_words: List["PunWord"] = Relationship(
        back_populates="pun", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def words(self):
        for pun_word in self.pun_words:
            yield pun_word.word

    def has_word(self, word):
        return self.pun_words.where(word=word).count() > 0

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
