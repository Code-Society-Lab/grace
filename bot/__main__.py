from os import getenv
from dotenv import load_dotenv
from logging import critical
from discord import errors
from bot.utils.extensions import get_extensions
from bot.grace import Grace

load_dotenv()

extensions = get_extensions()
token = getenv("DISCORD_TOKEN")

try:
    if token:
        grace_bot = Grace()
        grace_bot.load_extensions(extensions)
        grace_bot.run(token)
    else:
        critical("Token not defined. Add your token in '.env'")
except errors.LoginFailure as e:
    critical(f"{e}")
