from bin.database import reset
from bot import app

app.load("test", command_sync=False)

reset()
