"""Database configuration template

    This file is only a template to show how the `database.py` file should contain. You need, in the config directory,
    add you own database file called `database.py` and copy the content (except this comment) inside it. Then, you must
    change the values of each environement.

    ADAPTER
        The adapter is the name of the dialect used. THis can be `sqlite`, `mysql`, `postgresql`, `oracle` or `mssql`.
        You might need to also include the driver used.

    USER
        The should contain the username you're using to connect to the database.

    PASSWORD
        The password is your database user password.

    HOST
        The address of your sql server.

    PORT
        The port of your sql server.

    For further details you can consult https://docs.sqlalchemy.org/en/14/core/engines.html
"""


class Production:
    ADAPTER = "ADAPTER"
    USER = "USERNAME"
    PASSWORD = "PASSWORD"
    HOST = "localhost"
    PORT = 1234

    # This will be removed and build in config
    DATABASE = "grace_production"


class Development:
    ADAPTER = "ADAPTER"
    USER = "USER"
    PASSWORD = "PASSWORD"
    HOST = "localhost"
    PORT = 5432
    DATABASE = "grace_development"


class Test:
    ADAPTER = "ADAPTER"
    USER = "USERNAME"
    PASSWORD = "PASSWORD"
    HOST = "localhost"
    PORT = 1234
    DATABASE = "grace_test"
