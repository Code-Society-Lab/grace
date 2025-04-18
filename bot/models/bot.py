from sqlalchemy import Integer, Column, BigInteger
from grace.model import Model
from bot import app

class BotSettings(app.base, Model):
    """Configurable settings for each server"""
    __tablename__ = 'bot_settings'

    id = Column(Integer, primary_key=True)
    puns_cooldown = Column(BigInteger, default=60)

    @classmethod
    def settings(self):
        '''Since grace runs on only one settings record per bot,
        this is a semantic shortcut to get the first record.'''
        return self.first()
