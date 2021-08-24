from logging import critical
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from config.config import Config


class Application:
    _session = None

    def __init__(self):
        self.config = Config()
        self.token = getenv("DISCORD_TOKEN")

        self.engine = None
        self.base = declarative_base()

        self.load_database()

    @property
    def session(self):
        if Application._session is None:
            session = sessionmaker(bind=self.engine)
            Application._session = session()

        return Application._session

    def load_database(self):
        self.engine = create_engine(self.config.database_uri, echo=self.config.environment.SQLALCHEMY_ECHO)

        try:
            self.engine.connect()
        except OperationalError as e:
            critical(f"Unable to create the 'Application': {e}")
            exit()

    def unload_database(self):
        self.engine = None
        Application._session = None

    def reload_database(self):
        self.unload_database()
        self.load_database()

    def create_database(self):
        """Creates the database, if it's not already created, for the current environment"""
        if not database_exists(self.config.database_uri):
            create_database(self.config.database_uri)

    def drop_database(self):
        """Deletes the database, if it's not already deleted, for the current environment"""
        if not database_exists(self.config.database_uri):
            drop_database(self.config.database_uri)

    def create_tables(self):
        """Creates all the tables if they are not already created."""
        self.base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Deletes all the existing tables (Careful, all data will be lost!)"""
        self.base.metadata.drop_all(self.engine)
