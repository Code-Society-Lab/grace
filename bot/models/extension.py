from bot import app
from bot.classes.state import State
from grace.model import Field, Model
from lib.fields import EnumField


class Extension(Model):
    __tablename__ = "extensions"

    id: int | None = Field(default=None, primary_key=True)
    module_name: str = Field(nullable=False, unique=True)
    state: State = EnumField(State, default=State.ENABLED)

    @classmethod
    def by_state(cls, state):
        return cls.where(state=state)

    @property
    def name(self):
        return self.module_name.split(".")[-1].replace("_", " ").title()

    @property
    def short_module_name(self):
        return self.module_name.removeprefix("bot.extensions.")

    @property
    def module(self):
        return app.get_extension_module(self.module_name)

    def enable(self):
        self.state = State.ENABLED
        self.save()

    def disable(self):
        self.state = State.DISABLED
        self.save()

    def is_enabled(self):
        return self.state == State.ENABLED

    def should_be_loaded(self):
        load_only = app.config.environment.get("load_only")

        if not load_only:
            return self.is_enabled()

        names = (self.module_name, self.short_module_name)
        return self.is_enabled() and any(name in load_only for name in names)

    def __str__(self):
        return f"{self.id} | {self.module} - {self.state}"
