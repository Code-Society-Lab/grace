"""Contains environments database configurations"""


class Production:
    ADAPTER = "ADAPTER"
    USER = "USERNAME"
    PASSWORD = "PASSWORD"
    HOST = "localhost"
    PORT = 1234
    DATABASE = "grace_production"


class Development:
    ADAPTER = "sqlite"
    USER = ""
    PASSWORD = ""
    HOST = "localhost"
    PORT = 1234
    DATABASE = "grace_development"


class Test:
    ADAPTER = "ADAPTER"
    USER = "USERNAME"
    PASSWORD = "PASSWORD"
    HOST = "localhost"
    PORT = 1234
    DATABASE = "grace_test"
