from bot import app
from discord.ext import commands
from discord.ext.commands import CommandError


class ConfigRequiredError(CommandError):
    pass


class MissingRequiredConfig(ConfigRequiredError):
    def __init__(self, section_key, value_key):
        super().__init__(self, f"Missing config '{value_key}' in section '{section_key}'")


def cog_config_required(section_key, value_key):
    def decorator(cls):
        class Wrapper(cls):
            def __init__(self, *args, **kargs):
                self.required_config = app.config.get(section_key, value_key)
                super(Wrapper, self).__init__(*args, **kargs)

            async def cog_before_invoke(self, ctx):
                if not self.required_config:
                    raise MissingRequiredConfig()
        return Wrapper
    return decorator


def command_config_required(section_key, value_key):
    async def predicate(ctx):
        if not app.config.get(section_key, value_key):
            raise MissingRequiredConfig()
    return commands.check(predicate)
