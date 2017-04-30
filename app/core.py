from app import chargers, macbooks, thunderbolts, lost, found, slack_client


def get_equipment(equipment_id, equipment_type):
    '''
    Get equipment from database
    '''
    equipment = None
    if equipment_type in ["mac", "tmac", "macbook"]:
        equipment = chargers.find_one({"equipment_id": equipment_id})
    elif equipment_type in ["charger", "charge", "procharger"]:
        equipment = macbooks.find_one({"equipment_id": equipment_id})
    elif equipment_type in ["tb", "thunderbolt", "thunder"]:
        equipment = thunderbolts.find_one({"equipment_id": equipment_id})

    return equipment


def add_lost_equipment(owner, equipment_lost):
    '''
    Add a lost item to the database
    '''
    if not lost.find_one({"equipment": equipment_lost}):
        slack_profile = slack_client.api_call("users.info",
                                              user=owner)['user']["profile"]

        lost_item = {
            "equipment": equipment_lost,
            "owner": owner,
            "email": slack_profile["email"],
            "name": '{} {}'.format(slack_profile["first_name"],
                                   slack_profile["last_name"])
        }
        lost.insert_one(lost_item)
        return True
    return False


def add_found_equipment(submitter, equipment_found):
    '''
    Add a found item to the database
    '''
    if not found.find_one({"equipment": equipment_found}):
        slack_profile = slack_client.api_call("users.info",
                                              user=submitter)['user']["profile"]

        found_item = {
            "equipment": equipment_found,
            "submitter": submitter,
            "email": slack_profile["email"],
            "name": '{} {}'.format(slack_profile["first_name"],
                                   slack_profile["last_name"])
        }
        found.insert_one(found_item)
        return True
    return False


def remove_from_lost(equipment):
    lost.remove({"equipment": equipment})


def remove_from_found(equipment):
    found.remove({"equipment": equipment})


def search_found_equipment(equipment):
    return found.find_one({"equipment": equipment})


def search_lost_equipment(equipment):
    return lost.find_one({"equipment": equipment})


def notify_user_equipment_found(submitter, equipment_type):
    message = "The user <@{}> found your `{}`".format(
        submitter, equipment_type)
    slack_client.api_call("chat.postMessage", text=message, channel=submitter)


def build_search_reply_atachment(equipment, category):
    '''
    Returns a slack attachment to show a result
    '''
    return [{
        "text": "That {} belongs to {}".format(category, equipment["fellow_name"]),
                "fallback": "Equipment ID - {} | Owner - {}".format(equipment["equipment_id"], equipment["fellow_name"]),
                "color": "#4B719C",
                "fields": [
                    {
                        "title": "Equipment ID",
                        "value": "{}".format(equipment["equipment_id"]),
                        "short": "true"
                    },
                    {
                        "title": "Owner",
                        "value": "{}".format(equipment["fellow_name"]),
                        "short": "true"
                    }
        ]
    }]


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
