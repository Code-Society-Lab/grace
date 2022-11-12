from bot import app
from typing import Callable
from discord.ext import commands
from discord.ext.commands import CogMeta, Context, DisabledCommand


class ConfigRequiredError(DisabledCommand):
    """The base exception type for errors to required config check

    Inherit from `discord.ext.commands.CommandError` and can be handled like
    other CommandError exception in `on_command_error`
    """
    pass


class MissingRequiredConfigError(ConfigRequiredError):
    """Exception raised when a required configuration is missing.

    Inherit from `ConfigRequiredError`
    """

    def __init__(self, section_key: str, value_key: str):
        super().__init__(f"Missing config '{value_key}' in section '{section_key}'")


def cog_config_required(section_key: str, value_key: str) -> Callable:
    """Validates the presences of a given configuration before each
    invocation of a `discord.ext.commands.Cog` commands
    :param section_key:
        The required section key
    :param value_key:
        The required value key
    :raises TypeError:
        If the class is not a Cog
    """

    def wrapper(cls: CogMeta) -> CogMeta:
        async def _cog_before_invoke(self, _: Context):
            if not self.required_config:
                raise MissingRequiredConfigError(section_key, value_key)

        setattr(cls, "required_config", app.config.get(section_key, value_key))
        setattr(cls, "cog_before_invoke", _cog_before_invoke)

        return cls
    return wrapper


def command_config_required(section_key: str, value_key: str) -> Callable[[Context], bool]:
    """Validates the presences of a given configuration before running
    the `discord.ext.commands.Command`

    :param section_key:
        The required section key
    :param value_key:
        The required value key
    """

    async def predicate(_: Context) -> bool:
        if not app.config.get(section_key, value_key):
            raise MissingRequiredConfigError(section_key, value_key)
        return True
    return commands.check(predicate)
