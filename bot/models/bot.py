from grace.model import Model, Field


class BotSettings(Model):
    """Configurable settings for each server"""
    __tablename__ = 'bot_settings'

    id: int | None = Field(default=None, primary_key=True)
    puns_cooldown: int = Field(default=60)

    @classmethod
    def settings(self):
        '''Since grace runs on only one settings record per bot,
        this is a semantic shortcut to get the first record.'''
        return self.first()
