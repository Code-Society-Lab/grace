from sqlalchemy import Column, Integer, Text
from grace.model import Model, Field
from bot.classes.recurrence import Recurrence


class Thread(Model):
    __tablename__ = 'threads'

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str = Field(sa_type=Text)
    recurrence: Recurrence = Field(sa_column=Column(Integer))

    # @property
    # def recurrence(self) -> Recurrence:
    #     return Recurrence(self._recurrence)
    #
    # @recurrence.setter
    # def recurrence(self, new_recurrence: Recurrence):
    #     self._recurrence = new_recurrence.value

    @classmethod
    def find_by_recurrence(cls, recurrence: Recurrence) -> 'Recurrence':
        return cls.where(recurrence=recurrence.value)