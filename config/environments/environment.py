from enum import Enum, unique

from config.environments import Development, Production, Test


@unique
class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"

    def get_config(self):
        environments = {
            Environment.PRODUCTION: Production(),
            Environment.DEVELOPMENT: Development(),
            Environment.TEST: Test()
        }

        return environments.get(self)

    def __str__(self):
        return self.value