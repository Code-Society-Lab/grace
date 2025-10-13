from sqlalchemy import Column, Integer, Text

from bot.classes.recurrence import Recurrence
from grace.model import Field, Model


class Thread(Model):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str = Field(sa_type=Text)
    recurrence: Recurrence = Field(sa_column=Column(Integer))

    @classmethod
    def find_by_recurrence(cls, recurrence: Recurrence) -> "Recurrence":
        return cls.where(recurrence=recurrence.value)
