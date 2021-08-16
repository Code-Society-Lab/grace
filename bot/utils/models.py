import importlib
import pkgutil

from bot import models


def load_models():
    for module in pkgutil.walk_packages(models.__path__, f"{models.__name__}."):
        importlib.import_module(module.name)