from pymongo import MongoClient
from slackclient import SlackClient
from app.config import MONGODB_URI, BOT_TOKEN, SLACK_VERIFICATION_TOKEN
from app.myslackeventsapi import MySlackEventAdapter
from huey.contrib.minimal import MiniHuey


mongodb_client = MongoClient(MONGODB_URI)
db = mongodb_client.get_default_database()

# db collection
chargers = db.chargers
macbooks = db.macbooks
thunderbolts = db.thunderbolts
lost = db.lost
found = db.found
slack_handles = db.slack_handles

# slack client
slack_client = SlackClient(BOT_TOKEN)
slack_events_adapter = MySlackEventAdapter(SLACK_VERIFICATION_TOKEN,
                                           "/slack/events")

huey = MiniHuey()
