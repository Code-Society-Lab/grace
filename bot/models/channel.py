from grace.model import Field, Model
from sqlalchemy import UniqueConstraint


class Channel(Model):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("channel_name", "channel_id", name="uq_id_cn_cid"),
    )

    channel_name: str = Field(primary_key=True)
    channel_id: int = Field(primary_key=True)
