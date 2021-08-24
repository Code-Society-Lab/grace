from sqlalchemy import String, Column, ForeignKey, UniqueConstraint, BigInteger
from bot import app
from db.model import Model


class BotChannel(app.base, Model):
    __tablename__ = 'bot_channels'

    bot_id = Column(ForeignKey("bots.id"), primary_key=True)
    channel_name = Column(String, primary_key=True)
    channel_id = Column(BigInteger, primary_key=True)

    UniqueConstraint("bot_id", "channel_name", "channel_id", name="uq_bid_cn_cid")