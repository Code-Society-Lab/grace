import importlib
import inspect
import pkgutil
from bot import extensions


def get_extensions():
    for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
        if module.ispkg:
            imported = importlib.import_module(module.name)

            if not inspect.isfunction(getattr(imported, "setup", None)):
                continue

        yield module.name
