"""
This file contains the views for the bot which are really just event handlers
to different slack event types.
"""
from flask import request
from app import slack_events_adapter, slack_client, huey, logger
from huey import crontab
from app.controllers import MessageHandler
from app.helpers import generate_random_fortune
from functools import wraps
import re
import json
import random
import time


message_handler = MessageHandler()


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
                     f"{generate_random_fortune()}")
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
    message["text"] = re.sub(r"^<@.*?>\s?|\s?<@.{0,12}>$", "",
                             message.get("text"))
    response = message_handler.respond_to(message)
    logger.info(f"Sending {response.response_type} response to slack.")

    if response.response_type in ["RESPONSE_FORTUNE", "RESPONSE_GREETING",
                                  "RESPONSE_HELP"]:
        post_message(message["channel"], response.text,
                     attachments=response.attachments)
        return

    post_ephemeral_message(message["channel"], message["user"], response.text,
                           attachments=response.attachments)


@slack_events_adapter.server.route("/interactive", methods=["POST"])
def handle_interactive_message():
    payload = json.loads(request.form["payload"])

    if payload["callback_id"] == "notify_owner":
        # slack owner
        submitter = payload["user"]["id"]
        equipment = json.loads(payload["actions"][0]["value"])
        logger.info(f"Handling notify_owner request by "
                    f"<@{payload['user']['name']}> for "
                    f"{equipment['equipment_id']}")

        owner = equipment["owner_slack_id"]
        msg = f"Hi <@{owner}>! <@{submitter}> says they"\
            f" found your {equipment['type']}."
        logger.error(f"Attempting to notify owner {equipment['owner_name']} "
                     "that their equipment was found.")

        slack_response = post_message(owner, msg)
        if slack_response["ok"]:
            return f":green_heart: Thanks! We let {equipment['owner_name']} "\
                f"know you have their {equipment['type']}"
    return ":orange_heart: Oops! "\
        "We were unable to send the message. Something went wrong."


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
                                           attachments=attachments,
                                           as_user=True)
    if not slack_response["ok"]:
        logger.error(slack_response)
    return slack_response


def post_ephemeral_message(channel, user, message, attachments=None):
    """
    Call Slack API chat.postEphemeral method
    :param channel: Channel to post message to
    :param user: user to send message to
    :param message: message text to send
    :param attachments: message attachments
    :returns: response from slack api see \
    https://api.slack.com/methods/chat.postEphemeral
    """
    slack_response = slack_client.api_call("chat.postEphemeral",
                                           channel=channel,
                                           user=user, text=message,
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
    if message.get("subtype") is not None or message.get("bot_id") is not None:
        return False
    return True
