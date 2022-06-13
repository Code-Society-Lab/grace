from sqlalchemy import Integer, Column, String
from bot import app
from bot.classes.state import State
from db.model import Model


class Extension(app.base, Model):
    """Extension model (With SQLAlchemy ORM)"""
    __tablename__ = "extensions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    _state = Column("state", Integer, default=1)

    @property
    def state(self):
        return State(self._state)

    @state.setter
    def state(self, new_state):
        self._state = new_state.value

    @property
    def module(self):
        return app.get_extension_module(self.name)

    def is_enabled(self):
        return self.state == State.ENABLED

    def __str__(self):
        return f"{self.id} | {self.module} - {self.state}"
