from typing import TYPE_CHECKING
from emoji import emojize
from grace.model import Model, Field, Relationship

if TYPE_CHECKING:
    from bot.models.extensions.language.pun import Pun


class PunWord(Model):
    __tablename__ = "pun_words"

    id: int | None = Field(default=None, primary_key=True)
    pun_id: int = Field(foreign_key="puns.id")
    word: str = Field(max_length=255)
    emoji_code: str | None = Field(default=None, max_length=255)
    pun: "Pun" = Relationship(back_populates="pun_words")

    def emoji(self):
        return emojize(self.emoji_code, language="alias")
