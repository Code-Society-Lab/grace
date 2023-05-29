from bot.models.bot import BotSettings


def seed_database():
    BotSettings.create()
