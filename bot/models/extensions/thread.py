from sqlalchemy import Text

from bot.classes.recurrence import Recurrence
from grace.model import Field, Model
from lib.fields import EnumField

class Thread(Model):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str = Field(sa_type=Text)
    recurrence: Recurrence = EnumField(Recurrence, default=Recurrence.NONE)
    latest_thread = Column(String, nullable=True,)
    daily_reminder = Column(Boolean, nullable=True,)

    @property
    def recurrence(self) -> Recurrence:
        return Recurrence(self._recurrence)

    @recurrence.setter
    def recurrence(self, new_recurrence: Recurrence):
        self._recurrence = new_recurrence.value

    @classmethod
    def find_by_recurrence(cls, recurrence: Recurrence) -> "Recurrence":
        return cls.where(recurrence=recurrence.value)
