from pymongo import MongoClient
from slackclient import SlackClient
from app.config import MONGODB, BOT_TOKEN
import pymongo


mongodb_client = MongoClient()
db = mongodb_client[MONGODB]

# db collection
chargers = db.chargers
macbooks = db.macbooks
thunderbolts = db.thunderbolts
lost = db.lost
found = db.found

# slack client
slack_client = SlackClient(BOT_TOKEN)
