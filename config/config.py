from coloredlogs import install
from config import database
from os import getenv
from dotenv import load_dotenv
from config.environment import Environment
from pathlib import Path


class Config:
    """This class is the application configurations. It loads all the configuration for the given environment

    The config environment is chosen by checking the value of the `BOT_ENV` environment variable. If the variable
    is not set it will load with production by default.

    There can be only one config loaded at once. Which means thar if you instantiate a second or multiple Config
    object, they will all share the same environment. This is to say, that the config objects are identical.
    """

    __environment = None

    def __init__(self):
        base_path = Path()
        current_dir = base_path.cwd() / ".env"

        load_dotenv(current_dir)
        bot_env = self.get("BOT_ENV")

        if not Config.is_environment_loaded() and bot_env:
            Config.set_environment(Environment(bot_env))

    @property
    def database_uri(self):
        """Creates and returns the database URI"""
        database_uri = self.get("DATABASE_URL")

        if database_uri:
            # We need this .replace method because Heroku stores the database uri using
            # 'postgres' as the adapter name, but sqlalchemy does not support this anymore,
            # and requires the adapter to be declared as 'postgresql'
            return database_uri.replace("postgres://", "postgresql://", 1)
        else:
            return "{adapter}://{user}:{password}@{host}:{port}/grace_{database}".format(
                adapter=self.database_environment.ADAPTER,
                user=self.database_environment.USER,
                password=self.database_environment.PASSWORD,
                host=self.database_environment.HOST,
                port=self.database_environment.PORT,
                database=self.environment_name.lower()
            )

    @property
    def database_environment(self):
        databases = {
            'Development': database.Development,
            'Test': database.Test
        }

        return databases.get(self.environment_name, database.Production)

    @property
    def environment(self):
        return Config.__environment

    @property
    def environment_name(self):
        return type(self.environment).__name__

    @classmethod
    def set_environment(cls, environment):
        if isinstance(environment, Environment):
            cls.__environment = environment.get_config()
        else:
            raise EnvironmentError("You need to pass a valid environment. [Production, Development, Test]")

    @classmethod
    def is_environment_loaded(cls):
        return cls.__environment is not None

    @classmethod
    def get(cls, variable_name):
        """Returns the given environment variable"""
        return getenv(variable_name)
