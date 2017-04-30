from app import chargers, macbooks, thunderbolts, slack_client


def get_charger(charger_id):
    '''
    Get charger from database using id
    '''
    return chargers.find_one({"equipment_id": charger_id})


def get_macbook(macbook_id):
    '''
    Get charger from database using id
    '''
    return macbooks.find_one({"equipment_id": macbook_id})


def get_thunderbolt(thunderbolt_id):
    '''
    Get charger from database using id
    '''
    return thunderbolts.find_one({"equipment_id": thunderbolt_id})


def build_found_equipment_atachment(equipment, category):
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
    "A few bits tried to escape, we're catching them..."
    "It's still faster than slacking OPs :stuck_out_tongue_closed_eyes:",
    "Loading humorous message ... Please Wait",
    "Firing up the transmogrification device...",
    "Time is an illusion. Loading time doubly so.",
    "Slacking OPs for the information, this could take a while...",
    "Loading completed. Press F13 to continue.",
    "Looks like someone's been careless again :face_with_rolling_eyes:..."
]
