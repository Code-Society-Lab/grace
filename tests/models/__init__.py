import logging

logger = logging.getLogger(__name__)

from grace.database import up_migration

from bot import app
from db.seed import get_seed_modules

app.load("test")

app.command_sync = False
app.watch = False

app.drop_tables()
app.drop_database()

app.create_database()
up_migration(app, "head")

for seed_module in get_seed_modules():
    logger.info(f"Seeding {seed_module.__name__}")
    seed_module.seed_database()
