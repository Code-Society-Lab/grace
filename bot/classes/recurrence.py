from enum import Enum, unique


@unique
class Recurrence(Enum):
    NONE = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

    def __str__(self):
        return self.name.capitalize()

