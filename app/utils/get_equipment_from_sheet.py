"""
This script fetches tmacs, thunderbolts, dongles and chargers from the asset
spreadsheet and writes them to the equipment.json file. It dumps unmatched 
equipment i.e equipment that's yet to be matched to owner details such as
email and slack id. The next script to call after this one is the
match_equipment_to_owner.py script which should add the owner details from
slack.
"""

import json
import logging
import os

# import the gspread instance
from app.utils import gsheet as gc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

HOME_DIR = os.path.dirname(os.path.abspath(__file__))
EQUIPMENT_FILE = os.path.join(HOME_DIR, "equipment.json")


def get_all_items(sheet):
    """
    Function to return a list of all items in the master sheet
    Example:
        get_all_items('Master Sheet')

    :param sheet: The name of the sheet to use e.g 'Andela Asset Tracker'
    """

    # Get and write thunderbolts
    master_inventory_sheet = sheet.worksheet("Master Inventory List")

    # get a list of all assets in the andela_sheet
    and_items = master_inventory_sheet.get_all_values()

    data = {
        'macbooks': macbooks(and_items),
        'thunderbolts': thunderbolts(and_items),
        'chargers': mac_chargers(and_items),
        'dongles': dongles(and_items)
    }

    # create the equipments.json file
    json_file = open(EQUIPMENT_FILE, "w+")

    # write the data to the equipments .json file
    json_file.write(json.dumps(data))
    json_file.close()


def filter_items(sheet_data, device_type):
    """
    Function to filter and return a list of specific devices
    Works by filtering the sheet data for all devices with the same
    description.
    Example:
        filter_items(andelat_sheet_data, "Thunderbolt-Ethernet adapter")

    :param sheet_data: a list of the data in the andela master sheet being
    checked
    :param device_type: the device type under the description column
    :return: a lsi of the data for thunderbolts
    """

    filtered_items = []

    for list_item in sheet_data:
        if device_type in list_item:
            filtered_items.append(list_item)

    return filtered_items


def mac_chargers(and_items):
    """ return a list of thunderbolts with values: equipment_id, owner_name"""

    # filter_items(and_items, asset_item)
    logging.info('Retrieving chargers')

    # filter_items(and_items, asset_item)
    filtered_list = filter_items(and_items, "Macbook Charger")
    mac_chargers_list = []

    if filtered_list:
        for item in filtered_list:
            if not item[2] or not item[9]:
                continue
            col = {
                "equipment_id": item[2],
                "owner_name": item[9].strip(),
            }

            mac_chargers_list.append(col)

    logging.info('Retrieved %s chargers', len(mac_chargers_list))
    return mac_chargers_list


def thunderbolts(and_items):
    """ return a list of thunderbolts with values: equipment_id, owner_name"""

    # filter and return a list of thunderbolts
    logging.info('Retrieving thunderbolts')

    # filter_items(and_items, asset_item)
    filtered_list = filter_items(and_items, "Thunderbolt-Ethernet adapter")
    thunderbolts_list = []

    if filtered_list:

        for item in filtered_list:
            if not item[2] or not item[9]:
                continue
            col = {
                "equipment_id": item[2],
                "owner_name": item[9].strip(),
            }

            thunderbolts_list.append(col)

    logging.info('Retrieved %s thunderbolts', len(thunderbolts_list))
    return thunderbolts_list


def macbooks(sheet_data):
    logging.info('Retrieving Macbooks')

    # Get and dump mackbooks
    # filter_items(sheet, device_type)
    items = filter_items(sheet_data, "Training Macbook")
    items += filter_items(sheet_data, "Company Macbook")

    macbook_list = []

    if items:
        for item in items:
            if not item[2] or not item[9]:
                continue
            col = {
                "equipment_id": item[2],
                "serial_number": item[6],
                "owner_name": item[9].strip(),
                "owner_cohort": item[10].strip()
            }

            macbook_list.append(col)

    logging.info('Retrieved %s macbooks', len(macbook_list))
    return macbook_list


def dongles(sheet_data):
    logging.info('Retrieving Dongles')

    # Get and dump mackbooks
    # filter_items(sheet, device_type)
    items = filter_items(sheet_data, "Dongle")

    dongle_list = []

    if items:
        for item in items:
            if not item[2] or not item[9]:
                continue
            col = {
                "equipment_id": item[2],
                "owner_name": item[9].strip(),
            }

            dongle_list.append(col)

    logging.info('Retrieved %s dongles', len(dongle_list))
    return dongle_list


def main():
    sheet_name = "Asset Sheet"
    sheet = gc.open(sheet_name)
    get_all_items(sheet)


if __name__ == '__main__':
    main()
