from sqlalchemy import UniqueConstraint

from grace.model import Field, Model


class Channel(Model):
    __tablename__ = "channels"

    channel_name: str = Field(primary_key=True)
    channel_id: int = Field(primary_key=True)

    UniqueConstraint('channel_name', 'channel_id', name='uq_id_cn_cid')
