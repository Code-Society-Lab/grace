import importlib
import inspect
import os
import pkgutil
from bot import extensions


def get_extensions():
    for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
        if module.ispkg:
            imported = importlib.import_module(module.name)

            if not inspect.isfunction(getattr(imported, "setup", None)):
                continue

        yield module.name


def get_extensions_config():
    for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
        if not module.ispkg:
            config_path = f"{module.module_finder.path}/config.json"

            if os.path.exists(config_path):
                yield config_path


def get_extension(extension_name):
    for module in pkgutil.walk_packages(extensions.__path__, f"{extensions.__name__}."):
        if not module.ispkg and module.name.split(".")[-1] == extension_name:
            return module.name

