from logging import critical
from coloredlogs import install
from bot.config import Config
from bot.utils.extensions import get_extensions_config

install()
extension_configs = get_extensions_config()

try:
    CONFIG = Config.load_file("config.json")
    CONFIG.load_extensions_configs(extension_configs)

except IOError as e:
    critical(f"Error. {e}")
