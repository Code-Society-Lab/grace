from discord import Colour
from bot import app


def default_color() -> Colour | None:
    return Colour.from_str(app.bot.get("default_color"))
