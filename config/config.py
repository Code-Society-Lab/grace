from coloredlogs import install
from config import database
from os import getenv
from dotenv import load_dotenv
from config.environments import Production, Development, Test


class Config:
    """Environment configurations (Don't modify unless you know what you're doing).

        Attributes:
         environment (str): The environment used.
         database_uri (str): The database uri.
         database_environment (Production, Development, Test): The database used for the current environment.
    """
    environment = None

    def __init__(self):
        load_dotenv()

        if Config.environment is None:
            environments = {'development': Development(), 'test': Test()}
            Config.environment = environments.get(getenv("BOT_ENV"), Production())

        install(
            fmt="[%(asctime)s] %(programname)s %(levelname)s %(message)s",
            programname=f"({Config.environment.__class__.__name__})"
        )

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

        return databases.get(Config.environment.__class__.__name__, database.Production)
