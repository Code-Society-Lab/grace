from discord import Embed
from discord.ui import View
from typing import List


class ViewIterator:
    def __init__(self, collection):
        self._collection: List[View] = collection
        self._position = 0

    def current(self):
        return self._collection[self._position]

    def current_position(self):
        return self._position

    def items(self):
        return self._collection

    def get_item(self, index: int):
        if index in range(0, len(self._collection)):
            return self._collection[index]

    def add_item(self, item: View):
        self._collection.append(item)

    def next(self) -> View:
        if self.has_next():
            self._position += 1
        return self._collection[self._position]

    def previous(self) -> View:
        if self.has_previous():
            self._position -= 1
        return self._collection[self._position]

    def delete_previous(self):
        if self.has_previous():
            self._collection.pop(self._position - 1)

    def delete_current(self):
        if len(self._collection) > 0:
            self._collection.pop(self._position)

    def last(self) -> View:
        return self._collection[-1]

    def has_next(self) -> bool:
        return self._position + 1 < len(self._collection)

    def has_previous(self) -> bool:
        return self._position > 0


class EmbedIterator:
    def __init__(self, collection):
        self._collection: List[Embed] = collection
        self._position: int = 0

    def current(self):
        return self._collection[self._position]

    def next(self) -> Embed:
        if self.has_next():
            self._position += 1
        return self._collection[self._position]

    def previous(self) -> Embed:
        if self.has_previous():
            self._position -= 1
        return self._collection[self._position]

    def last(self) -> Embed:
        return self._collection[-1]

    def has_next(self) -> bool:
        return self._position + 1 < len(self._collection)

    def has_previous(self) -> bool:
        return self._position > 0
