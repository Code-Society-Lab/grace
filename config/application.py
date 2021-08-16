from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import Config


class Application:
    _session = None

    def __init__(self):
        self.config = Config()
        self.token = getenv("DISCORD_TOKEN")

        self.engine = create_engine(self.config.database_uri, echo=self.config.environment.SQLALCHEMY_ECHO)
        self.base = declarative_base()

        self.engine.connect()
        self.base.metadata.create_all(self.engine)

    @property
    def session(self):
        if Application._session is None:
            session = sessionmaker(bind=self.engine)
            Application._session = session()

        return Application._session

    def create_tables(self):
        """Creates all the tables if they are not already created."""
        self.base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Delete all the existing tables (Careful, all data will be lost!)"""
        self.base.metadata.drop_all(self.engine)
