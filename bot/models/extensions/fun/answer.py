from typing import Optional

from grace.model import Field, Model


class Answer(Model):
    __tablename__ = "answers"

    id: Optional[int] = Field(default=None, primary_key=True)
    answer: str = Field(max_length=255)
