from slackclient import SlackClient
from app.config import BOT_TOKEN, SLACK_VERIFICATION_TOKEN
from app.myslackeventsapi import MySlackEventAdapter
from huey.contrib.minimal import MiniHuey

# slack client
slack_client = SlackClient(BOT_TOKEN)
slack_events_adapter = MySlackEventAdapter(SLACK_VERIFICATION_TOKEN,
                                           "/slack/events")

huey = MiniHuey()
