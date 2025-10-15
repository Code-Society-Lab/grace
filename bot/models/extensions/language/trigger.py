from typing import List

from emoji import emojize

from bot.models.extensions.language.trigger_word import TriggerWord
from grace.model import Field, Model, Relationship


class Trigger(Model):
    __tablename__ = "triggers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, unique=True)
    positive_emoji_code: str = Field(max_length=255)
    negative_emoji_code: str = Field(max_length=255)

    trigger_words: List[TriggerWord] = Relationship(
        back_populates="trigger", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def words(self):
        for trigger_word in self.trigger_words:
            yield trigger_word.word

    @property
    def positive_emoji(self):
        return emojize(self.positive_emoji_code, language="alias")

    @property
    def negative_emoji(self):
        return emojize(self.negative_emoji_code, language="alias")

    def add_trigger_word(self, trigger_word):
        TriggerWord(trigger_id=self.id, word=trigger_word).save()

    def remove_trigger_word(self, trigger_word):
        TriggerWord.where(trigger_id=self.id, word=trigger_word).first().delete()
