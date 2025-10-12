from sqlalchemy import Column, Integer, String, Text
from grace.model import Model
from bot import app
from bot.classes.recurrence import Recurrence


class Thread(app.base, Model):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True)
    title = Column(
        String,
        nullable=False,
    )
    content = Column(
        Text,
        nullable=False,
    )
    _recurrence = Column('recurrence', Integer, nullable=False, default=0)

    @property
    def recurrence(self) -> Recurrence:
        return Recurrence(self._recurrence)

    @recurrence.setter
    def recurrence(self, new_recurrence: Recurrence):
        self._recurrence = new_recurrence.value

    @classmethod
    def find_by_recurrence(cls, recurrence: Recurrence) -> 'Recurrence':
        return cls.where(_recurrence=recurrence.value)
