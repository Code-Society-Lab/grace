import importlib
import pkgutil
from bot import models


def load_models():
    """Import all models in the `bot/models` folder."""

    for module in pkgutil.walk_packages(models.__path__, f"{models.__name__}."):
        if not module.ispkg:
            importlib.import_module(module.name)