from logging import info, warning, error, critical
from discord import Embed
from datetime import datetime


def log(bot, title, description):
    return LogHelper(bot, title, description)


class LogHelper:
    COLORS_BY_LOG_LEVEL = {
        "critical": critical,
        "error": "",
        "warning": "",
        "info": "",
    }

    def __init__(self, bot, title, description, log_level=None):
        self.bot = bot
        self.channel = bot.get_channel_by_name("moderation_logs")
        self.embed = Embed(
            title=title,
            description=description,
            color=self.get_color_by_log_level(log_level),
            timestamp=datetime.utcnow()
        )

    def get_color_by_log_level(self, log_level):
        return self.COLORS_BY_LOG_LEVEL.get(log_level, self.bot.default_color)

    def add_field(self, name, value):
        self.embed.add_field(
            name=name,
            value=value,
            inline=False
        )

    def __await__(self):
        yield from self.channel.send(embed=self.embed).__await__()
