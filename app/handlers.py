# coding: UTF-8
import re
import random
import time
import json
from slackbot.bot import respond_to
from app.core import get_equipment, loading_messages, build_search_reply_atachment, add_lost_equipment, search_found_equipment, remove_from_lost, search_lost_equipment, add_found_equipment, notify_user_equipment_found, remove_from_found


@respond_to('hello$|hi$|hey$|aloha$|bonjour$', re.IGNORECASE)
def hello_reply(message):
    time.sleep(1)
    message.reply('Hello stranger. What can I do you for?')


@respond_to('love', re.IGNORECASE)
def love_reply(message):
    love_replies = [
        "I know.", ":heart:", "I like you as a friend",
        "So does my cousin @slackbot.", "That’s weird. Why do you love 'U'",
        "OK, what do you need?"
    ]
    time.sleep(1)
    message.reply(random.choice(love_replies))


@respond_to('thanks|thank', re.IGNORECASE)
def gratitude_reply(message):
    time.sleep(1)
    message.reply("No problemo Guillermo")


@respond_to("(find|get|search|retrieve) (mac|tmac|macbook|charger|charge|procharger|tb|thunderbolt|thunder).*?(\d+)", re.IGNORECASE)
def find_equipment(message, command, equipment_type, equipment_id):
    time.sleep(1)
    message.reply(random.choice(loading_messages))
    time.sleep(2)

    attachments = []
    equipment_type = equipment_type.strip().lower()
    print equipment_type
    # get equipment from db
    equipment = get_equipment(int(equipment_id), equipment_type)

    if equipment:
        attachments.extend(
            build_search_reply_atachment(equipment,
                                            "item"))
        time.sleep(1)
        print attachments
        message.send_webapi('', json.dumps(attachments))
        return
    else:
        time.sleep(1)
        message.reply("We were unable to find an "
                      "item by the id {} :snowman_without_snow:".format(equipment_id))


@respond_to("lost (mac|tmac|macbook|charger|charge|procharger|tb|thunderbolt|thunder).*?(\d+)")
def report_lost(message, equipment_type, equipment_id):
    '''
    Report an item has been lost
    '''
    # get equipment from db
    equipment = get_equipment(int(equipment_id), equipment_type)

    if equipment:
        owner = message.body['user']

        # try to find if equipment is in the found collection before adding it
        found_equipment = search_found_equipment(equipment)
        if found_equipment:
            time.sleep(1)
            message.reply("Woohoo!:tada: The user <@{}> reported they "
                          "found your {}.\n"
                          "We're marking this item as found.".format(
                              found_equipment['submitter'],
                              equipment_type))
            remove_from_found(found_equipment)
            return
        else:
            if add_lost_equipment(owner, equipment):
                time.sleep(1)
                message.reply("Added `{}-{}` to our database. We'll slack you "
                              "in case anyone finds it "
                              ":envelope_with_arrow:".format(equipment_type,
                                                             equipment_id))
            else:
                time.sleep(1)
                message.reply("The item `{0}-{1}` is already in our "
                              "database. Send `found {0} {1}` "
                              "if you meant to report you found it.".format(
                                  equipment_type,
                                  equipment_id))
    else:
        time.sleep(1)
        message.reply("That item doesn't exist in our database "
                      "and thus can't be reported as lost.")


@respond_to("found (mac|tmac|macbook|charger|charge|procharger|tb|thunderbolt|thunder).*?(\d+)")
def submit_found(message, equipment_type, equipment_id):
    '''
    Submit a found item
    '''
    # get equipment from db
    equipment = get_equipment(int(equipment_id), equipment_type)

    if equipment:
        submitter = message.body['user']
        # check if item is in lost collection
        equipment_in_lost = search_lost_equipment(equipment)

        if equipment_in_lost:
            time.sleep(1)
            notify_user_equipment_found(submitter, equipment_type)
            message.reply("Woohoo!:tada: We've notified the owner <@{}> "
                          "that you found their {}.\nI would pat your "
                          "back if I had any hands."
                          " Keep being awesome :clap:".format(equipment_in_lost["owner"],
                                                              equipment_type)
                          )
            remove_from_lost(equipment_in_lost)
        else:
            if add_found_equipment(submitter, equipment):
                time.sleep(1)
                message.reply("Added `{}-{}` to our database. We'll slack the "
                              "owner when they report it missing. "
                              ":outbox_tray:. Thank you".format(equipment_type,
                                                                equipment_id))
            else:
                time.sleep(1)
                message.reply("The item `{0}-{1}` is already in our "
                              "database. Send `lost {0} {1}` "
                              "if you meant to report you lost it.".format(
                                  equipment_type,
                                  equipment_id))

    else:
        time.sleep(1)
        message.reply("That item doesn't exist in our database "
                      "and thus can't be reported as found.")
