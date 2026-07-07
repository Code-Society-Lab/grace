from grace.model import Field, Model


class Answer(Model):
    __tablename__ = "answers"

    id: int | None = Field(default=None, primary_key=True)
    answer: str = Field(max_length=255)
