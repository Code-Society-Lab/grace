from enum import IntEnum, unique


@unique
class State(IntEnum):
    DISABLED = 0
    ENABLED = 1

    def __str__(self):
        return self.name.capitalize()

