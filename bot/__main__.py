from logging import critical
from discord import errors
from bot import app
from bot.grace import Grace
from bot.utils.extensions import get_extensions
from bot.utils.models import load_models

load_models()
extensions = get_extensions()

try:
    if app.token:
        app.create_tables()

        grace_bot = Grace()
        grace_bot.load_extensions(extensions)
        grace_bot.run(app.token)
    else:
        critical("Token not defined. Add your token in '.env'")
except errors.LoginFailure as e:
    critical(f"{e}")
