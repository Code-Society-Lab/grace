from config import database


class Production:
    COLOREDLOGS_LOG_LEVEL = "INFO"
    SQLALCHEMY_ECHO = False
