from typing import List, TypeVar, Generic, Iterator, Optional

T = TypeVar("T")


class BidirectionalIterator(Generic[T]):
    """An iterator allows to go forward and backward in a list, modify the list during iteration and obtain the item
    at the current position in the list.

    :param collection: An optional collection of items, default to an empty List.
    :type collection: Optional[List[T]]
    """
    def __init__(self, collection: Optional[List[T]]):
        self.__collection: List[T] = collection or []
        self.__position: int = 0

    @property
    def current(self) -> T:
        """Returns the item at the current position in the list.

        :return: The current value
        :rtype: T
        """
        return self.__collection[self.__position]

    @property
    def first(self) -> T:
        """Returns the first element in the list.

        :return: The first element
        :rtype: T
        """
        return self.__collection[0]

    @property
    def last(self) -> T:
        """Returns the last item in the list.

        :return: The first element
        :rtype: T
        """
        return self.__collection[-1]

    def add(self, item: T):
        """Adds and item at the end of the list.

        :param item: An Item
        :type: T
        """
        self.__collection.append(item)

    def remove(self, item: T):
        """Removes the first occurrence of the item from a list.

        :param item: An item
        :type: T
        """
        self.__collection.remove(item)

    def next(self) -> T:
        """Returns the next item in the list if it has any next item or return the current item.

        :return: The next and current item
        :rtype: T
        """
        if self.has_next():
            self.__position += 1
        return self.current

    def previous(self) -> T:
        """Returns the previous item in the list if it has any previous item or return the current item.

        :return: The previous or current item
        :rtype: T
        """
        if self.has_previous():
            self.__position -= 1
        return self.current

    def has_next(self) -> bool:
        """Returns true if there is any next item relative to the current position.

        :return: True if there is any next item or False.
        :rtype: bool
        """
        return self.__position + 1 < len(self.__collection)

    def has_previous(self) -> bool:
        """Returns true if there's any previous item relative to the current position.

        :return: True if there is any previous item or False
        :rtype: bool
        """
        return self.__position > 0

    def __len__(self) -> int:
        return len(self.__collection)

    def __iter__(self) -> Iterator[T]:
        return iter(self.__collection)
