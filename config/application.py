from configparser import SectionProxy
from importlib import import_module
from pkgutil import walk_packages, ModuleInfo
from logging import basicConfig, critical
from logging.handlers import RotatingFileHandler
from types import ModuleType
from typing import Generator, Any, Union, IO, Dict
from coloredlogs import install
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker, Session, DeclarativeMeta
from sqlalchemy_utils import database_exists, create_database, drop_database
from bot import models, extensions
from config.config import Config
from pathlib import Path


class Application:
    """This class is the core of the application In other words, this class that manage the database, the application
    environment and loads the configurations.

    Note: The database uses SQLAlchemy ORM (https://www.sqlalchemy.org/).
    """

    __config: Union[Config, None] = None
    __session: Union[Session, None] = None
    __base = declarative_base()  # type: DeclarativeMeta

    template_path: Path = Path("bin/templates/default.database.template.cfg")
    database_config_path: Path = Path("config/database.cfg")

    @property
    def base(self):
        return self.__base

    def __init__(self):
        if not self.database_config_path.exists():
            self._generate_database_config()

        self.__token: str = self.config.get("discord", "token")
        self.__engine: Union[Engine, None] = None

        self.command_sync: bool = True

    @property
    def token(self) -> str:
        return self.__token

    @property
    def session(self) -> Session:
        """Instantiate the session for querying the database."""

        if not self.__session:
            session: sessionmaker = sessionmaker(bind=self.__engine)
            self.__session = session()

        return self.__session

    @property
    def config(self) -> Config:
        if not self.__config:
            self.__config = Config()

        return self.__config

    @property
    def bot(self) -> SectionProxy:
        return self.config.client

    @property
    def extension_modules(self) -> Generator[ModuleInfo, Any, None]:
        """Generate the extensions modules"""

        for module in walk_packages(extensions.__path__, f"{extensions.__name__}."):
            if module.ispkg:
                imported: ModuleType = import_module(module.name)

                if not hasattr(imported, "setup"):
                    continue
            yield module

    @property
    def database_infos(self) -> Dict[str, str]:
        return {
            "dialect": self.session.bind.dialect.name,
            "database": self.session.bind.url.database
        }

    @property
    def database_exists(self):
        return database_exists(self.config.database_uri)

    def get_extension_module(self, extension_name) -> Union[ModuleInfo, None]:
        """Return the extension from the given extension name"""

        for extension in self.extension_modules:
            if extension.name == extension_name:
                return extension
        return None

    def load(self, environment: str, command_sync: bool = True):
        """Sets the environment and loads all the component of the application"""

        self.command_sync = command_sync
        self.config.set_environment(environment)
        self.load_logs()
        self.load_models()
        self.load_database()

    @staticmethod
    def load_models():
        """Import all models in the `bot/models` folder."""

        for module in walk_packages(models.__path__, f"{models.__name__}."):
            if not module.ispkg:
                import_module(module.name)

    def load_logs(self):
        file_handler: RotatingFileHandler = RotatingFileHandler(
            f"logs/{self.config.current_environment}.log",
            maxBytes=10000,
            backupCount=5
        )

        basicConfig(
            level=self.config.environment.get("log_level"),
            format="[%(asctime)s] %(funcName)s %(levelname)s %(message)s",
            handlers=[file_handler],
        )

        install(
            self.config.environment.get("log_level"),
            fmt="[%(asctime)s] %(programname)s %(funcName)s %(module)s %(levelname)s %(message)s",
            programname=self.config.current_environment,
        )

    def load_database(self):
        """Loads and connects to the database using the loaded config"""

        self.__engine = create_engine(
            self.config.database_uri,
            echo=self.config.environment.getboolean("sqlalchemy_echo")
        )

        if self.database_exists:
            try:
                self.__engine.connect()
            except OperationalError as e:
                critical(f"Unable to load the 'database': {e}")

    def unload_database(self):
        """Unloads the current database"""

        self.__engine = None
        self.__session = None

    def reload_database(self):
        """Reload the database. This function can be use in case there's a dynamic environment change."""

        self.unload_database()
        self.load_database()

    def create_database(self):
        """Creates the database for the current loaded config"""

        self.load_database()
        create_database(self.config.database_uri)

    def drop_database(self):
        """Drops the database for the current loaded config"""

        self.load_database()
        drop_database(self.config.database_uri)

    def create_tables(self):
        """Creates all the tables for the current loaded database"""

        self.load_database()
        self.base.metadata.create_all(self.__engine)

    def drop_tables(self):
        """Drops all the tables for the current loaded database"""

        self.load_database()
        self.base.metadata.drop_all(self.__engine)

    def _generate_database_config(self):
        template: IO = open(self.template_path, mode='rt', encoding='utf-8')
        config: IO = open(self.database_config_path, mode='wt', encoding='utf-8')

        config.write(template.read())

        template.close()
        config.close()
