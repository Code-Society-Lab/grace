import importlib
import pkgutil
from db import seeds


def get_seeds():
    for module in pkgutil.walk_packages(seeds.__path__, f"{seeds.__name__}."):
        if not module.ispkg:
            yield importlib.import_module(module.name)