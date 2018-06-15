from app.config import HOME_DIR
import jmespath
import json

all_equipment = json.loads(open(HOME_DIR + "/utils/equipment.json", "r").
                           read())


def find_equipment_by_id(id_, equipment_type):
    """
    Find equipment that matches given id from equipment store
    :param id_: :string: equipment id eg. TB/0034
    :param equipment_type: specific equipment store to look in should be one
    of: chargers, thunderbolts, macbooks or dongles
    :return: dict of found equipment or None if no equipment by that id is
    found
    """
    return jmespath.search(f"{equipment_type}[?equipment_id=='{id_}']",
                           all_equipment)


def find_equipment_by_owner_id(owner_id, equipment_type):
    """
    Find equipment that matches given owner_id from equipment store
    :param owner_id: owner slackid eg. U1234567
    :param equipment_type: specific equipment store to look in should be one
    of: chargers, thunderbolts, macbooks or dongles
    :return: dict of found equipment or None if no equipment by that id is
    found
    """
    return jmespath.search(f"{equipment_type}[?owner_slack_id=='{owner_id}']",
                           all_equipment)
