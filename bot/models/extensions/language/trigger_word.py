from typing import TYPE_CHECKING, Optional

from grace.model import Field, Model, Relationship

if TYPE_CHECKING:
    from .trigger import Trigger


class TriggerWord(Model):
    __tablename__ = "trigger_words"

    trigger_id: int = Field(foreign_key="triggers.id", primary_key=True)
    word: str = Field(max_length=255, primary_key=True)

    trigger: Optional["Trigger"] = Relationship(
        back_populates="trigger_words", sa_relationship_kwargs={"lazy": "selectin"}
    )
