from grace.database import up_migration

from bot import app

app.load("test")

app.drop_tables()
app.drop_database()

app.create_database()
up_migration(app, "head")
