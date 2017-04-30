# coding: UTF-8
import re
import random
import time
import json
from slackbot.bot import respond_to
from app.core import get_charger, get_macbook, get_thunderbolt, loading_messages, build_found_equipment_atachment


@respond_to('hello$|hi$|hey$|aloha$|bonjour$', re.IGNORECASE)
def hello_reply(message):
    time.sleep(1)
    message.reply('Bonjour and howdy stranger. What can I do you for?')


@respond_to('(tb|thunderbolt|thunder).*?(\d+)', re.IGNORECASE)
def find_thunderbolt(message, equipment_type, equipment_id):
    message.reply(random.choice(loading_messages))
    time.sleep(2)

    attachments = []
    # get thunderbolt from db
    thunderbolt = get_thunderbolt(int(equipment_id))

    if thunderbolt:
        attachments.extend(
            build_found_equipment_atachment(thunderbolt,
                                            "thunderbolt"))
        time.sleep(1)
        print attachments
        message.send_webapi('', json.dumps(attachments))
        return
    else:
        time.sleep(1)
        message.reply("We were unable to find a "
                      "thunderbolt by the id {} :zap:".format(equipment_id))
