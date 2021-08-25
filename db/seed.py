"""Database seed modules

All seed modules are located in the `db/seeds` folder. They need a  ̀seed_database` function. Without this function,
the modules will be skipped and thus the seeding will not work correctly.

Template Ex.
```
# import your models

def seed_database():
    # Create an instance of the model with the desired data
    Model(name="a name")

    # Save the model
    model.save()
```
"""

import importlib
import pkgutil
from db import seeds


def get_seeds():
    """Generate all seed modules"""

    for module in pkgutil.walk_packages(seeds.__path__, f"{seeds.__name__}."):
        if not module.ispkg:
            yield importlib.import_module(module.name)