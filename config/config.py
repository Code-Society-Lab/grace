from ast import literal_eval
from os import path
from dotenv import load_dotenv
from configparser import ConfigParser, BasicInterpolation
from sqlalchemy.engine import URL
from re import match


class EnvironmentInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values.

    With this literal '${NAME}', the config will process the value from the given
    environment variable and use it as it's value in the config.

    This includes exported environment variable (ex. 'export MY_VAR=...') and
    variable in '.env' files.

    Usage example.
        token = ${MY_SECRET_VAR}

    In the example above, token will take the value of the environment variable
    called 'MY_SECRET_VAR'. In case 'MY_SECRET_VAR' doesn't exist, the value will
    not be evaluated.

    """

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
        self.__config = ConfigParser(interpolation=EnvironmentInterpolation())

        self.__config.read("config/settings.cfg")
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
        return self.__config[f"database.{self.__environment}"]

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
        # I don't know if it's the desired behavior. Do we really want our config to convert out data?
        value = self.__config.get(section_key, value_key, fallback=fallback)

        if value and match(r"^[\d.]*$|^(?:True|False)*$", value):
            return literal_eval(value)
        return value

    def set_environment(self, environment):
        if environment in ["production", "development", "test"]:
            self.__environment = environment
        else:
            raise EnvironmentError("You need to pass a valid environment. [Production, Development, Test]")
