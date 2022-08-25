from bot import app
from discord.ext import commands
from discord.ext.commands import CommandError, CogMeta, Cog


class ConfigRequiredError(CommandError):
    """The base exception type for errors to required config check

    Inherit from `discord.ext.commands.CommandError` and can be handled like
    other CommandError exception in `on_command_error`
    """
    pass


class MissingRequiredConfig(ConfigRequiredError):
    """Exception raised when a required configuration is missing.

    Inherit from `ConfigRequiredError`
    """

    def __init__(self, section_key, value_key):
        super().__init__(f"Missing config '{value_key}' in section '{section_key}'")


def cog_config_required(section_key, value_key):
    """Validates the presences of a given configuration before each
    invocation of a `discord.ext.commands.Cog` commands

    :param section_key:
        The required section key
    :param value_key:
        The required value key
    :raises TypeError:
        If the class is not a Cog
    """

    def decorator(cls):
        class Wrapper(cls):
            def __init__(self, *args, **kargs):
                if not isinstance(cls, CogMeta):
                    raise TypeError("The class needs to be a cog")

                self.required_config = app.config.get(section_key, value_key)
                super().__init__(*args, **kargs)

            async def cog_before_invoke(self, ctx):
                if not self.required_config:
                    raise MissingRequiredConfig(section_key, value_key)

            def __new__(cls, *args, **kwargs):
                cls.__cog_name__ = getattr(cls.__base__, "__cog_name__")
                cls.__cog_description__ = getattr(cls.__base__, "__cog_description__")
                cls.__cog_settings__ = getattr(cls.__base__, "__cog_settings__")

                return super().__new__(cls, *args, **kwargs)
        return Wrapper

    return decorator


def command_config_required(section_key, value_key):
    """Validates the presences of a given configuration before running
    the `discord.ext.commands.Command`

    :param section_key:
        The required section key
    :param value_key:
        The required value key
    """

    async def predicate(ctx):
        if not app.config.get(section_key, value_key):
            raise MissingRequiredConfig(section_key, value_key)

    return commands.check(predicate)
