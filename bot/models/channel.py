from sqlalchemy import String, Column, UniqueConstraint, BigInteger
from grace.model import Model
from bot import app


class Channel(app.base, Model):
    __tablename__ = 'channels'

    channel_name = Column(String(255), primary_key=True)
    channel_id = Column(BigInteger, primary_key=True)

    UniqueConstraint("channel_name", "channel_id", name="uq_id_cn_cid")
