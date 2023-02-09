from bot import app
from typing import Callable, Optional
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

    def __init__(self, section_key: str, value_key: str, message: Optional[str] = None):
        base_error_message = f"Missing config '{value_key}' in section '{section_key}'"
        super().__init__(f"{base_error_message}\n{message}" if message else base_error_message)


def cog_config_required(section_key: str, value_key: str, message: Optional[str] = None) -> Callable:
    """Validates the presences of a given configuration before each
    invocation of a `discord.ext.commands.Cog` commands
    :param section_key:
        The required section key
    :param value_key:
        The required value key
    :param message:
        The optional message/instruction if missing required config
    :raises TypeError:
        If the class is not a Cog
    """

    def wrapper(cls: CogMeta) -> CogMeta:
        async def _cog_before_invoke(self, _: Context):
            if not self.required_config:
                raise MissingRequiredConfigError(section_key, value_key, message)

        setattr(cls, "required_config", app.config.get(section_key, value_key))
        setattr(cls, "cog_before_invoke", _cog_before_invoke)

        return cls
    return wrapper


def command_config_required(section_key: str, value_key: str, message: Optional[str] = None) -> Callable[[Context], bool]:
    """Validates the presences of a given configuration before running
    the `discord.ext.commands.Command`

    :param section_key:
        The required section key
    :param value_key:
        The required value key
    :param message:
        The optional message/instruction if missing required config
    :raises TypeError:
        If the class is not a Cog
    """

    async def predicate(_: Context) -> bool:
        if not app.config.get(section_key, value_key):
            raise MissingRequiredConfigError(section_key, value_key, message)
        return True
    return commands.check(predicate)
