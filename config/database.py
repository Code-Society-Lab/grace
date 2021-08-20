"""Contains environments database configurations"""


class Production:
    ADAPTER = "postgresql"
    USER = "ruby"
    PASSWORD = "Malassi12"
    HOST = "localhost"
    PORT = 5433
    DATABASE = "grace_production"


class Development:
    ADAPTER = "postgresql"
    USER = "ruby"
    PASSWORD = "Malassi12"
    HOST = "localhost"
    PORT = 5433
    DATABASE = "grace_development"


class Test:
    ADAPTER = "postgresql"
    USER = "ruby"
    PASSWORD = "Malassi12"
    HOST = "localhost"
    PORT = 5433
    DATABASE = "grace_test"
