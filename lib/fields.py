from typing import Type

from sqlalchemy import Column
from sqlalchemy.types import Integer, TypeDecorator
from sqlmodel import Field


class IntEnumType(TypeDecorator):
    impl = Integer
    cache_ok = True

    def __init__(self, enumtype):
        self.enumtype = enumtype
        super().__init__()

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        return value.value

    def process_result_value(self, value, dialect):
        return self.enumtype(value) if value is not None else None


def EnumField(enum_cls: Type, **kwargs):
    sa_column = Column(IntEnumType(enum_cls))
    return Field(sa_column=sa_column, **kwargs)
