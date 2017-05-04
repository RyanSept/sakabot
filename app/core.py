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
    lost.delete_one({"equipment": equipment})


def remove_from_found(equipment):
    found.delete_one({"equipment": equipment})


def search_found_equipment(equipment):
    return found.find_one({"equipment": equipment})


def search_lost_equipment(equipment):
    return lost.find_one({"equipment": equipment})


def notify_user_equipment_found(submitter, owner, equipment_type):
    message = "The user <@{}> found your `{}`".format(
        submitter, equipment_type)
    slack_client.api_call("chat.postMessage", text=message, channel=owner)


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


def get_help_message():
    return [
        {
            "text": "Sakabot helps you search, find or report a lost item "
            "whether it be your macbook, thunderbolt or charger.\n *USAGE*",
            "color": "#4B719C",
            "mrkdwn_in": ["fields", "text"],
            "fields": [
                {
                    "title": "Searching for an item's owner",
                    "value": "To search for an item's owner send "
                    "`find charger|mac|thunderbolt <item_id>` "
                    "to _@sakabot_.\n eg. `find charger 41`"
                },
                {
                    "title": "Reporting that you've lost an item",
                    "value": "When you lose an item, there's a chance that "
                    "somebody has found it and submitted it to Sakabot. "
                    "In that case we'll tell you who found it, otherwise, "
                    "we'll slack you in case anyone reports they found it. To "
                    "report an item as lost send `lost charger|mac|thunderbolt <item_id>` to _@sakabot._"
                    "\n eg. `lost thunderbolt 33`"
                },
                {
                    "title": "Submit a found item",
                    "value": "When you find a lost item you can report that "
                    "you found it and in case a user had reported it lost, "
                    "we'll slack them immediately telling them you found it. "
                    "To report that you found an item send `found charger|mac|thunderbolt <item_id>` to _@sakabot_"
                    "\n eg. `found mac 67`"
                }
            ],
        }
    ]


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
