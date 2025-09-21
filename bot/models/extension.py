from sqlalchemy import Integer, Column, String
from grace.model import Model
from bot import app
from bot.classes.state import State


class Extension(app.base, Model):
    """Extension model (With SQLAlchemy ORM)"""
    __tablename__ = "extensions"

    id = Column(Integer, primary_key=True)
    module_name = Column(String(255), nullable=False, unique=True)
    _state = Column("state", Integer, default=1)

    @classmethod
    def by_state(cls, state):
        return cls.where(_state=state.value)

    @property
    def name(self):
        return self.module_name.split(".")[-1].replace("_", " ").title()

    @property
    def state(self):
        return State(self._state)

    @state.setter
    def state(self, new_state):
        self._state = new_state.value

    @property
    def module(self):
        return app.get_extension_module(self.module_name)

    def is_enabled(self):
        return self.state == State.ENABLED

    def __eq__(self, other):
        if isinstance(other, str):
            return self.module_name == other
        if isinstance(other, Extension):
            return self.module_name == other.module_name
        return False

    def __str__(self):
        return f"{self.id} | {self.module} - {self.state}"
