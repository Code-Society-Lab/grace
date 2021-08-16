from enum import Enum, unique


@unique
class State(Enum):
    DISABLED = 0
    ENABLED = 1

    def __str__(self):
        self.name.capitalize()

