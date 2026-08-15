from grace.model import Field, Model


class WidgetState(Model):
    __tablename__ = "widget_states"

    key: str = Field(primary_key=True)
    value: str = Field(nullable=False)
