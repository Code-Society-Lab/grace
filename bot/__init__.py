from logging import critical
from coloredlogs import install
from bot.config import Config

install()

try:
    CONFIG = Config.load_file("config.json")
except IOError as e:
    critical(f"Error. {e}")
