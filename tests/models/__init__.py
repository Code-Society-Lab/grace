from bot import app
from logging import info, error
from db.seed import get_seeds


app.load("test")

app.command_sync = False
app.watch = False

app.drop_tables()
app.drop_database()

app.create_database()
app.create_tables()

for seed_module in get_seeds():
    info(f"Seeding {seed_module.__name__}")
    seed_module.seed_database()
