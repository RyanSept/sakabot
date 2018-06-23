from slackclient import SlackClient
from app.config import BOT_TOKEN, SLACK_VERIFICATION_TOKEN, LOG_LEVEL
from app.myslackeventsapi import MySlackEventAdapter
from huey.contrib.minimal import MiniHuey

import logging


# slack client
slack_client = SlackClient(BOT_TOKEN)
slack_events_adapter = MySlackEventAdapter(SLACK_VERIFICATION_TOKEN,
                                           "/slack/events")

logger = logging.getLogger(name=__name__)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d}\n%(levelname)s - %(message)s\n")

stream_handler.setFormatter(formatter)
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream_handler)


huey = MiniHuey()
