from bot.models.channel import Channel


def seed_database():
    """The seed function. This function is needed in order for the seed to be executed"""
    initial_channels = {
        "introductions": 916658807789199390,
        "roles": 823239926023192596,
        "info": 825404191492276225,
        "rules": 823183118902362132,
        "welcome": 823178343943897091,
        "moderation_logs": 932748961863831592
    }

    for channel_name in initial_channels:
        Channel.create(channel_name=channel_name, channel_id=initial_channels.get(channel_name))

