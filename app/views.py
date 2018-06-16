"""
This file contains the views for the bot which are really just event handlers
to different slack event types.
"""
from flask import request
from app import slack_events_adapter, slack_client, huey
from huey import crontab
from app.config import HOME_DIR
from app.controllers import MessageHandler
from functools import wraps
import re
import json
import random
import time
import logging

logger = logging.getLogger(name=__name__)
message_handler = MessageHandler()

# loading messages
loading_messages = json.loads(open(HOME_DIR + "/utils/fortunes.json", "r").
                              read())


@slack_events_adapter.on("message")
def handle_message_event(event_data):
    if not is_valid_message_event(event_data):
        return

    logger.info(f"Handling message event.\n{event_data}")
    message = event_data["event"]

    response = message_handler.respond_to(message)
    logger.debug(response)
    if response.response_type == "RESPONSE_SEARCH_EQUIPMENT":
        post_message(message["channel"],
                     f"{random.choice(loading_messages)['quote']}")
        time.sleep(0.5)

    logger.info(f"Sending {response.response_type} response to slack.")
    post_message(message["channel"], response.text,
                 attachments=response.attachments)


@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    if not is_valid_message_event(event_data):
        return

    logger.info(f"Handling message event.\n{event_data}")
    message = event_data["event"]

    # Remove mention from message.
    message["text"] = re.sub(r"!find\s?<@.*>\s?", "", message.get("text"))
    response = message_handler.respond_to(message)
    logger.info(f"Sending {response.response_type} response to slack.")
    post_message(message["channel"], response.text,
                 attachments=response.attachments)


@slack_events_adapter.server.route("/interactive", methods=["POST"])
def handle_interactive_message():
    payload = json.loads(request.form["payload"])
    print(payload)
    if payload["callback_id"] == "notify_owner":
        pass
    return ""


def post_message(channel, message, attachments=None):
    """
    Call Slack API chat.postMessage method
    :param channel: Channel to post message to
    :param message: message text to send
    :param attachments: message attachments
    :returns: response from slack api see \
    https://api.slack.com/methods/chat.postMessage
    """
    slack_response = slack_client.api_call("chat.postMessage",
                                           channel=channel, text=message,
                                           attachments=attachments)
    if not slack_response["ok"]:
        logger.error(slack_response)
    return slack_response


def is_valid_message_event(event_data):
    """
    Validate message event to check if it's not something like a file or a
    bot message etc.
    :param event_data: Slack event
    """
    message = event_data["event"]
    if message.get("subtype") is None:
        return True
    return False
