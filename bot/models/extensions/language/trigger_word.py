from grace.model import Model, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .trigger import Trigger


class TriggerWord(Model):
    __tablename__ = "trigger_words"

    # trigger_id = Column(ForeignKey("triggers.id"), primary_key=True)
    # word = Column(String(255), primary_key=True)
    trigger_id: int = Field(foreign_key="triggers.id", primary_key=True)
    word: str = Field(max_length=255, primary_key=True)

    trigger: Optional["Trigger"] = Relationship(back_populates="trigger_words")
