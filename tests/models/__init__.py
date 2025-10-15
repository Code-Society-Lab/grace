from logging import info

from bot import app
from db.seed import get_seed_modules
from grace.database import up_migration

app.load("test")

app.command_sync = False
app.watch = False

app.drop_tables()
app.drop_database()

app.create_database()
app.create_tables()

up_migration(app, "head")

for seed_module in get_seed_modules():
    info(f"Seeding {seed_module.__name__}")
    seed_module.seed_database()
