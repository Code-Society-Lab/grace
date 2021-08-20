from logging import critical
from bot.json_config import JsonConfig
from bot.utils.extensions import get_extensions_config
from config.application import Application

app = Application()
extension_configs = get_extensions_config()

try:
    CONFIG = JsonConfig.load_file("config.json")
    CONFIG.load_extensions_configs(extension_configs)
except IOError as e:
    critical(f"Error. {e}")
