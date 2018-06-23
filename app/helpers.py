from app.config import HOME_DIR
import random
import json


# loading messages
fortunes = json.loads(open(HOME_DIR + "/utils/fortunes.json", "r").
                      read())


def generate_random_hex_color():
    '''
    Generate random hex color
    '''
    def r(): return random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(), r(), r()))


def build_search_equipment_attachment(equipment, equipment_type,
                                      add_notify_owner_btn=False):
    '''
    Returns a slack attachment to show a result
    :param equipment: equipment object
    :param equipment_type: type of equipment eg. dongle, thunderbolt, macbook
    :param add_notify_owner_btn: <optional> add a notify owner button to the
    result
    :return: dict attachment to send in slack response
    '''
    # equipment_type is in canonical form (plural)
    # so we get everything up to the last letter
    equipment_type = equipment_type[:-1]
    equipment["type"] = equipment_type
    attachment = {
        "text": f"{equipment['owner_name']}'s {equipment_type}",
        "fallback": f"Equipment ID - {equipment['equipment_id']} | Owner - {equipment['owner_name']}",
        "color": generate_random_hex_color(),
        "fields": [{
            "title": "Equipment ID",
            "value": f"{equipment['equipment_id']}",
            "short": "true"
        },
            {
            "title": "Owner",
            "value": f"<@{equipment['owner_slack_id']}>",
            "short": "true"
        }
        ]
    }
    if add_notify_owner_btn:
        attachment.update(
            {
                "callback_id": "notify_owner",
                "actions": [
                    {
                        "name": "notify_owner",
                        "text": "Notify the owner you have their equipment",
                        "type": "button",
                        "value": json.dumps(equipment),
                        "confirm": {
                            "title": "Are you sure?",
                            "text": f"Clicking 'Yes' will send a message to "
                            f"{equipment['owner_name']} "
                            f"telling them you found their {equipment_type}.",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }]})
    return attachment


def generate_random_fortune():
    return random.choice(fortunes)['quote']


# deprecated
loading_messages = [
    "We're testing your patience.",
    "A few bits tried to escape, we're catching them...",
    "It's still faster than slacking OPs :stuck_out_tongue_closed_eyes:",
    "Loading humorous message ... Please Wait",
    "Firing up the transmogrification device...",
    "Time is an illusion. Loading time doubly so.",
    "Slacking OPs for the information, this could take a while...",
    "Loading completed. Press F13 to continue.",
    "Oh boy, more work! :face_with_rolling_eyes:..."
]
