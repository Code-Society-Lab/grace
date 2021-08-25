from bot.models.bot import Bot
from bot.models.bot_channel import BotChannel


def seed_database():
    """The seed function. This function is needed in order for the seed to be executed"""

    grace = Bot(
        name="Grace",
        prefix="::",
        description="Grace is the official Code Society Discord bot.",
        default_color_code="0xfffffe",
        welcome_message="Hi {member_name}! Welcome to the **Code Society**.\n\nBefore posting please:\n    - Take a moment to read the <#{info_id}> and the <#{rules_id}>.\n    - Choose some <#{roles_id}>.\n    - Feel free to introduce yourself in <#{intro_id}>."
    )

    initial_channels = {
        "introductions": 825410663437303868,
        "roles": 823239926023192596,
        "info": 825404191492276225,
        "rules": 823183118902362132,
        "welcome": 823178343943897091
    }

    grace.save()

    for channel_name in initial_channels:
        BotChannel(bot_id=grace.id, channel_name=channel_name, channel_id=initial_channels.get(channel_name)).save()

