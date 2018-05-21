import random


def generate_random_hex_color():
    '''
    Generate random hex color
    '''
    r = lambda: random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(), r(), r()))


def build_search_reply_atachment(equipment, equipment_type):
    '''
    Returns a slack attachment to show a result
    :param equipment: equipment object
    :param equipment_type: type of equipment eg. dongle, thunderbolt, macbook
    :return: dict attachment to send in slack response
    '''
    return [{
        "text": f"{equipment['owner_name']}'s {equipment_type[:-1]}",
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
    }]


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
