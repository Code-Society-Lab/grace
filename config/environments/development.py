from config import database


class Development:
    COLOREDLOGS_LOG_LEVEL = "DEBUG"
    SQLALCHEMY_ECHO = True
