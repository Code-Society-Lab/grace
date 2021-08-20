import logging

from coloredlogs import install
from config import database
from os import getenv
from dotenv import load_dotenv
from config.environments.environment import Environment


class Config:
    """Environment configurations (Don't modify unless you know what you're doing).

        Attributes:
         environment (str): The environment used.
         database_uri (str): The database uri.
         database_environment (Production, Development, Test): The database used for the current environment.
    """
    __environment = None

    def __init__(self):
        load_dotenv()

        if not Config.is_environment_loaded():
            Config.set_environment(Environment(getenv("BOT_ENV")))

    @property
    def database_uri(self):
        """Creates and returns the database URI"""

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
        """"Returns the database environment configs"""

        databases = {
            'Development': database.Development,
            'Test': database.Test
        }

        return databases.get(self.environment.__class__.__name__, database.Production)

    @property
    def environment(self):
        return Config.__environment

    @classmethod
    def set_environment(cls, environment):
        if isinstance(environment, Environment):
            cls.__environment = environment.get_config()
            cls.load_logs()
        else:
            raise EnvironmentError("You need to pass a valid environment")

    @classmethod
    def is_environment_loaded(cls):
        return cls.__environment is not None

    @classmethod
    def load_logs(cls):
        install(
            fmt="[%(asctime)s] %(programname)s %(levelname)s %(message)s",
            programname=f"({Config.__environment.__class__.__name__})"
        )
