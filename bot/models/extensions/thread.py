from sqlalchemy import Text

from bot.classes.recurrence import Recurrence
from grace.model import Field, Model
from lib.fields import EnumField


class Thread(Model):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str = Field(sa_type=Text)
    recurrence: Recurrence = EnumField(
        Recurrence, default=Recurrence.NONE, nullable=False
    )
    latest_thread: int
    daily_reminder: bool

    @classmethod
    def find_by_recurrence(cls, recurrence: Recurrence) -> "Recurrence":
        return cls.where(recurrence=recurrence.value)
