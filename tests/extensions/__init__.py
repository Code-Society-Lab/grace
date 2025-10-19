from bot import app
from grace.database import up_migration

app.load("test")

app.drop_tables()
app.drop_database()

app.create_database()
up_migration(app, "head")
