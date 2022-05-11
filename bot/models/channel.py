from sqlalchemy import String, Column, UniqueConstraint, BigInteger, Integer
from bot import app
from db.model import Model


class Channel(app.base, Model):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    channel_name = Column(String(255))
    channel_id = Column(BigInteger)

    UniqueConstraint("channel_name", "channel_id", name="uq_id_cn_cid")
