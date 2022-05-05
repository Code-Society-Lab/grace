from os import getenv
from dotenv import load_dotenv
from configparser import ConfigParser


class Config:
    """This class is the application configurations. It loads all the configuration for the given environment

    The config environment is chosen by checking the value of the `BOT_ENV` environment variable. If the variable
    is not set it will load with production by default.

    There can be only one config loaded at once. Which means thar if you instantiate a second or multiple Config
    object, they will all share the same environment. This is to say, that the config objects are identical.
    """

    def __init__(self):
        self.__environment = None
        self.__config = ConfigParser()

        self.__config.read("config/settings.client.cfg")  # Do we want multiple client? Could change with the env?
        self.__config.read("config/database.cfg")
        self.__config.read("config/environment.cfg")

        load_dotenv(".env")

    @property
    def database_uri(self):
        """Creates and returns the database URI"""
        # TODO SQLite is supported by SQLAlchmey, thus we need to rework the wat it currently works to get ride of .env
        database_uri = getenv("DATABASE_URL")

        if database_uri:
            # We need this .replace method because Heroku stores the database uri using
            # 'postgres' as the adapter name, but sqlalchemy does not support this anymore,
            # and requires the adapter to be declared as 'postgresql'
            return database_uri.replace("postgres://", "postgresql://", 1)
        else:
            # TODO The port should be optional. Maybe we'll need ot create a more complex builder for managing that.
            return "{adapter}://{user}:{password}@{host}:{port}/{database}".format(
                adapter=self.database["adapter"],
                user=self.database["user"],
                password=self.database["password"],
                host=self.database["host"],
                port=self.database["port"],
                database=f"{self.client['name']}_{self.__environment}"
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

    def get(self, section_key, value_key):
        return self.__config.get(section_key, value_key)

    def set_environment(self, environment):
        if environment in ["production", "development", "test"]:
            self.__environment = environment
        else:
            raise EnvironmentError("You need to pass a valid environment. [Production, Development, Test]")
