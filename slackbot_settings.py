import os

API_TOKEN = os.getenv("BOT_TOKEN")
ERRORS_TO = os.getenv('ERRORS_TO')
DEFAULT_REPLY = "Sorry but I didn't understand you. Type `help` for assistance"
PLUGINS = [
    'app',
]
