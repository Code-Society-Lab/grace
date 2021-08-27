from enum import Enum, unique
from config.environments import Development, Production, Test


@unique
class Environment(Enum):
    """The enum contains the available environment configuration"""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"

    def get_config(self):
        """Returns the environment config"""

        environments = {
            Environment.PRODUCTION: Production(),
            Environment.DEVELOPMENT: Development(),
            Environment.TEST: Test()
        }

        return environments.get(self)

    def __str__(self):
        """String representation"""

        return self.value
