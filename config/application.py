from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from config.config import Config


class Application:
    def __init__(self):
        self.config = Config()
        self.token = getenv("DISCORD_TOKEN")

        self.engine = create_engine(self.config.database_uri, echo=self.config.environment.SQLALCHEMY_ECHO)
        self.base = declarative_base()

        self.engine.connect()
        self.base.metadata.create_all(self.engine)

    def create_tables(self):
        """Creates all the tables if they are not already created."""
        self.base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Delete all the existing tables (Careful, all data will be lost!)"""
        self.base.metadata.drop_all(self.engine)
