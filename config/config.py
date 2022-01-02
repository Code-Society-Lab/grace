from coloredlogs import install
from config import database
from os import getenv
from dotenv import load_dotenv
from config.environment import Environment


class Config:
    """This class is the application configurations. It loads all the configuration for the given environment

    The config environment is chosen by checking the value of the `BOT_ENV` environment variable. If the variable
    is not set it will load with production by default.

    There can be only one config loaded at once. Which means thar if you instantiate a second or multiple Config
    object, they will all share the same environment. This is to say, that the config objects are identical.
    """

    # The config environment
    # If you plan on accessing the environment, use the `environment` property
    __environment = None

    def __init__(self):
        load_dotenv()

        bot_env = self.get("BOT_ENV")

        if not Config.is_environment_loaded():
            if bot_env:
                environment = Environment(bot_env)
            else:
                environment = Environment("production")

            Config.set_environment(environment)

    @property
    def database_uri(self):
        """Creates and returns the database URI"""
        database_uri = self.get("DATABASE_URL")

        if database_uri:
            return database_uri
        else:
            return "{adapter}://{user}:{password}@{host}:{port}/{database}".format(
                adapter=self.database_environment.ADAPTER,
                user=self.database_environment.USER,
                password=self.database_environment.PASSWORD,
                host=self.database_environment.HOST,
                port=self.database_environment.PORT,
                database=self.database_environment.DATABASE
            )

    @property
    def database_environment(self):
        """"Returns the current environment database configs"""

        databases = {
            'Development': database.Development,
            'Test': database.Test
        }

        return databases.get(self.environment.__class__.__name__, database.Production)

    @property
    def environment(self):
        """Return the loaded current environment"""

        return Config.__environment

    @classmethod
    def set_environment(cls, environment):
        """Set the config environment"""

        if isinstance(environment, Environment):
            cls.__environment = environment.get_config()
            cls.load_logs()
        else:
            raise EnvironmentError("You need to pass a valid environment. [Production, Development, Test]")

    @classmethod
    def is_environment_loaded(cls):
        """Returns `True` if the environment is loaded and false if the environment is not loaded"""

        return cls.__environment is not None

    @classmethod
    def load_logs(cls):
        """Loads the logging system"""

        install(
            fmt="[%(asctime)s] %(programname)s %(levelname)s %(message)s",
            programname=f"({Config.__environment.__class__.__name__})"
        )

    @classmethod
    def get(cls, variable_name):
        """Returns the given environment variable"""

        return getenv(variable_name)
