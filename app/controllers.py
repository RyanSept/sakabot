from app.models import find_equipment_by_id, find_equipment_by_owner_id
from app.helpers import build_search_reply_atachment
import re

EQUIPMENT_TYPE_CANONICAL_NAME = {}
EQUIPMENT_TYPE_CANONICAL_NAME["macbook"] = EQUIPMENT_TYPE_CANONICAL_NAME[
    "tmac"] = EQUIPMENT_TYPE_CANONICAL_NAME["mac"] = "macbooks"
EQUIPMENT_TYPE_CANONICAL_NAME["charger"] = EQUIPMENT_TYPE_CANONICAL_NAME[
    "charge"] = EQUIPMENT_TYPE_CANONICAL_NAME["procharger"] = "chargers"
EQUIPMENT_TYPE_CANONICAL_NAME["tb"] = EQUIPMENT_TYPE_CANONICAL_NAME[
    "thunderbolt"] = EQUIPMENT_TYPE_CANONICAL_NAME["thunder"] = "thunderbolts"
EQUIPMENT_TYPE_CANONICAL_NAME["dongle"] = "dongles"


class MessageHandler:
    """
    This class handles mappings for messages to handlers for
    them based on a regex match. To add a new message handler, add its regex to
    self.responses as the value with the key as the function to handle it.
    """

    def __init__(self):
        self.responses = {
            "^hello$|^hi$|^hey$|^aloha$|^bonjour$": self.hello_reply,
            "(?:find|get|search|retrieve)\s(<@.*>.*?|my|me)\s(mac|tmac|macbook|charger|charge|procharger|tb|thunderbolt|thunder|dongle)": self.search_equipment_by_owner_reply,
            "(?:find|get|search|retrieve)\s(\w+\/.*)": self.search_equipment_reply,
            "love": self.love_reply,
            "thanks|thank": self.gratitude_reply,
            "help": self.help_reply,
        }

    def respond_to(self, message):
        """
        Pass message to handler based on regex match

        :param message: slack event message
        :return: HTTP response on success or failure
        """
        found_match = False
        for pattern in self.responses:
            handler = self.responses[pattern]
            match = re.compile(pattern, re.IGNORECASE).search(message["text"])
            if match:
                found_match = True
                break
        if found_match:
            return handler(message, *match.groups())
        return self.default_reply(message)

    def hello_reply(self, message):
        return Response(f"Hello <@{message['user']}>! :tada:",
                        "RESPONSE_GREETING")

    def search_equipment_reply(self, message, equipment_id):
        equipment_id = equipment_id.upper().strip()
        equipment = None

        for equipment_store in ["dongles", "chargers", "macbooks",
                                "thunderbolts"]:
            equipment = find_equipment_by_id(equipment_id, equipment_store)
            if equipment is not None:
                break

        if equipment is None:
            return Response("Sorry. I did not find any equipment by that "
                            "id :slightly_frowning_face:",
                            "RESPONSE_SEARCH_EQUIPMENT")
        attachments = build_search_reply_atachment(equipment,
                                                   equipment_store)
        return Response("", "RESPONSE_SEARCH_EQUIPMENT",
                        attachments=attachments)

    def search_equipment_by_owner_reply(self, message, owner_id,
                                        equipment_type):
        # sanitize
        if owner_id in ["me", "my"]:
            owner_id = message["user"]
        else:
            owner_id = owner_id[owner_id.index("<@") + 2: owner_id.index(">")]
        equipment_type = EQUIPMENT_TYPE_CANONICAL_NAME[equipment_type]

        equipment = find_equipment_by_owner_id(owner_id, equipment_type)
        if equipment is None:
            return Response(f"Sorry. I did not find any {equipment_type}"
                            f" belonging to <@{owner_id}> "
                            ":slightly_frowning_face:",
                            "RESPONSE_SEARCH_EQUIPMENT")
        attachments = build_search_reply_atachment(equipment,
                                                   equipment_type)

        return Response("", "RESPONSE_SEARCH_EQUIPMENT",
                        attachments=attachments)

    def love_reply(self, message):
        return Response("OK, what do you need?", "RESPONSE_LOVE")

    def gratitude_reply(self, message):
        return Response("No problemo", "RESPONSE_GRATITUDE")

    def help_reply(self, message):
        return Response("HELP< YOU'RE GONNA NEED SOMEBODY!", "RESPONSE_HELP")

    def default_reply(self, message):
        return Response("Sorry but I didn't understand you."
                        " Try sending `help`.", "RESPONSE_DEFAULT")


class Response:
    """
    Response object returned by MessageHandler message handling methods
    """

    def __init__(self, text, response_type, attachments=None):
        self.text = text
        self.response_type = response_type
        self.attachments = attachments

    def __repr__(self):
        return f"Response('{self.text}', '{self.response_type}', "\
            f"'{self.attachments}')"
