import configparser
from os import getenv, path
from dotenv import load_dotenv
from configparser import ConfigParser
from sqlalchemy.engine import URL


class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return path.expandvars(value)


class Config:
    """This class is the application configurations. It loads all the configuration for the given environment

    The config environment is chosen by checking the value of the `BOT_ENV` environment variable. If the variable
    is not set it will load with production by default.

    There can be only one config loaded at once. Which means thar if you instantiate a second or multiple Config
    object, they will all share the same environment. This is to say, that the config objects are identical.
    """

    def __init__(self):
        load_dotenv(".env")

        self.__environment = None
        self.__config = ConfigParser(interpolation=EnvInterpolation())

        self.__config.read(f"config/settings.cfg")
        self.__config.read("config/database.cfg")
        self.__config.read("config/environment.cfg")

    @property
    def database_uri(self):
        if self.database.get("url"):
            return self.database.get("url")

        return URL.create(
            self.database["adapter"],
            self.database.get("user"),
            self.database.get("password"),
            self.database.get("host"),
            self.database.get("port"),
            self.database.get("database", f"{self.client['name']}_{self.__environment}")
        )

    @property
    def database(self):
        return self.__config[self.__environment]

    @property
    def client(self):
        return self.__config["client"]

    @property
    def environment(self):
        return self.__config[self.__environment]

    @property
    def current_environment(self):
        return self.__environment

    def get(self, section_key, value_key, fallback=None):
        return self.__config.get(section_key, value_key, fallback=fallback)

    def set_environment(self, environment):
        if environment in ["production", "development", "test"]:
            self.__environment = environment
        else:
            raise EnvironmentError("You need to pass a valid environment. [Production, Development, Test]")
