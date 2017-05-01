from pymongo import MongoClient
from slackclient import SlackClient
from app.config import MONGODB_URI, BOT_TOKEN

mongodb_client = MongoClient(MONGODB_URI)
db = mongodb_client["saka"]

# db collection
chargers = db.chargers
macbooks = db.macbooks
thunderbolts = db.thunderbolts
lost = db.lost
found = db.found

# slack client
slack_client = SlackClient(BOT_TOKEN)
