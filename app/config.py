import os
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
# slack bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
# get from env or use default mongo uri
MONGODB_URI = os.getenv('MONGODB_URI') or "mongodb://127.0.0.1:27017/saka"
