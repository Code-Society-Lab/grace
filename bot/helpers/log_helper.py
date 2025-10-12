from discord import Embed, Color
from datetime import datetime


def info(title, description):
    # Will be deprected in favor of notice
    return LogHelper(title, description, "info")


def notice(title, description):
    return LogHelper(title, description, "info")


def warning(title, description):
    return LogHelper(title, description, "warning")


def danger(title, description):
    return LogHelper(title, description, "danger")


class LogHelper:
    __DEFAULT_COLOR = Color.from_rgb(0, 123, 255)
    COLORS_BY_LOG_LEVEL = {
        "danger": Color.from_rgb(220, 53, 69),
        "warning": Color.from_rgb(255, 193, 7),
        "info": __DEFAULT_COLOR,
    }

    def __init__(self, title, description, log_level="info"):
        self.embed = Embed(
            title=title,
            description=description,
            color=self.COLORS_BY_LOG_LEVEL.get(log_level, self.__DEFAULT_COLOR),
            timestamp=datetime.utcnow(),
        )

    def add_field(self, name, value):
        self.embed.add_field(name=name, value=value, inline=False)

    async def send(self, channel):
        await channel.send(embed=self.embed)
