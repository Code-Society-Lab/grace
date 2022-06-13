import importlib
import inspect
import pkgutil
from logging import critical
from coloredlogs import install
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from bot import models, extensions
from config.config import Config


class Application:
    """This class is the core of the application In other words, this class that manage the database, the application
    environment and loads the configurations.

    Note: The database uses SQLAlchemy ORM (https://www.sqlalchemy.org/).
    """

    __config = None
    __session = None

    def __init__(self):
        self.__token = self.config.get("discord", "token")
        self.__engine = None
        self.__base = declarative_base()

    @property
    def token(self):
        return self.__token

    @property
    def base(self):
        return self.__base

    @property
    def session(self):
        """Instantiate the session for querying the database."""
        if not Application.__session:
            session = sessionmaker(bind=self.__engine)
            Application.__session = session()

        return Application.__session

    @property
    def config(self):
        if not Application.__config:
            Application.__config = Config()

        return Application.__config

    @property
    def bot(self):
        return self.config.client

    @property
    def extensions(self):
        """Generate the extensions modules"""

        for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
            if module.ispkg:
                imported = importlib.import_module(module.name)

                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue

            yield module.name

    def get_extension(self, extension_name):
        """Return the extension from the given extension name"""

        for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
            if not module.ispkg and module.name.split(".")[-1] == extension_name:
                return module.name

    def load(self, environment):
        """Sets the environment and loads all the component of the application"""
        self.config.set_environment(environment)

        self.load_logs()
        self.load_models()
        self.load_database()

    def load_models(self):
        """Import all models in the `bot/models` folder."""
        for module in pkgutil.walk_packages(models.__path__, f"{models.__name__}."):
            if not module.ispkg:
                importlib.import_module(module.name)

    def load_logs(self):
        install(
            self.config.environment.get("log_level"),
            fmt="[%(asctime)s] %(programname)s %(levelname)s %(message)s",
            programname=f"{self.bot['name'].capitalize()} ({self.config.current_environment})"
        )

    def load_database(self):
        """Loads and connects to the database using the loaded config"""
        self.__engine = create_engine(
            self.config.database_uri,
            echo=self.config.environment.getboolean("sqlalchemy_echo"))

        if database_exists(self.config.database_uri):
            try:
                self.__engine.connect()
            except OperationalError as e:
                critical(f"Unable to load the 'database': {e}")

    def unload_database(self):
        """Unloads the current database"""
        Application.__engine = None
        Application.__session = None

    def reload_database(self):
        """Reload the database. This function can be use in case there's a dynamic environment change."""
        self.unload_database()
        self.load_database()

    def create_database(self):
        """Creates the database for the current loaded config"""
        if not database_exists(self.config.database_uri):
            self.load_database()
            create_database(self.config.database_uri)

    def drop_database(self):
        """Drops the database for the current loaded config"""
        if not database_exists(self.config.database_uri):
            self.load_database()
            drop_database(self.config.database_uri)

    def create_tables(self):
        """Creates all the tables for the current loaded database"""
        self.load_database()
        self.__base.metadata.create_all(self.__engine)

    def drop_tables(self):
        """Drops all the tables for the current loaded database"""
        self.load_database()
        self.__base.metadata.drop_all(self.__engine)
