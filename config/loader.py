from collections import namedtuple
from importlib import import_module
from os.path import commonpath
from pathlib import Path
from types import ModuleType
from typing import Generator

ModuleInfo = namedtuple("ModuleInfo", ["name", "file"])


def walk_packages(package: ModuleType) -> Generator[ModuleInfo, None, None]:
    """Walk through the packages and yield the module info."""

    if package.__file__ is None:
        raise OSError(f"{package} is not a package. Perhaps the '__init__.py' file is missing.")

    for module_absolute_path in Path(package.__path__[0]).glob('**/*.py'):
        module_path = module_absolute_path.relative_to(commonpath([__file__, package.__file__]))
        module_path = module_path.as_posix().replace('/', '.').removesuffix('.py')

        yield ModuleInfo(module_path, module_absolute_path.name)


def load_models():
    """Import all models in the `bot/models` folder."""
    from bot import models

    for module in walk_packages(models):
        import_module(module.name)
