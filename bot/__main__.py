from os import getenv
from dotenv import load_dotenv
from logging import critical
from discord import errors
from bot.utils.extensions import get_extensions
from bot.grace import Grace

load_dotenv()

token = getenv("DISCORD_TOKEN")
extensions = get_extensions()

try:
    if token:
        grace_bot = Grace()
        grace_bot.load_extensions(extensions)
        grace_bot.run(token)
    else:
        critical("Token not defined. Add your token in '.env'")
except errors.LoginFailure as e:
    critical(f"{e}")
