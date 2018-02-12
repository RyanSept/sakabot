import json
import logging

# import the gspread instance
from app.utils import gsheet as gc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

def get_all_items(sheet):
    """
    Function to return a list of all items in the master sheet
    Example:
        get_all_items('Master Sheet')

    :param sheet: The name of the sheet to use e.g 'Andela Asset Tracker'
    """

     # Get and write thunderbolts
    master_inventory_sheet = gc.open(sheet).worksheet("Master  Inventory List")

    # get a list of all assets in the andela_sheet
    and_items = master_inventory_sheet.get_all_values()

    data = {
            'macbooks': macbooks(and_items),
            'thunderbolts': thunderbolts(and_items),
            'chargers': mac_chargers(and_items),
            'dongles': dongles(and_items)
    }

    # create the equipments.json file
    json_file = open("app/utils/assets/equipment.json", "w")

    # write the data to the equipments .json file
    json_file.write(json.dumps(data))
    json_file.close()

def filter_items(sheet_data, device_type):
    """
    Function to filter and return a list of specific devices
    Works by filtering the sheet data for all devices with the same description.
    Example:
        filter_items(andelat_sheet_data, "Thunderbolt-Ethernet adapter")

    :param sheet_data: a list of the data in the andela master sheet being checked
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
    logging.info('Working on the Training Macbook Chargers worksheet')

    # filter_items(and_items, asset_item)
    filtered_list = filter_items(and_items, "Macbook Charger")
    mac_chargers_list = []

    if filtered_list:
        for item in filtered_list:
            col = {
                "equipment_id": item[2] ,
                "owner_name": item[8].strip(),
            }

            mac_chargers_list.append(col)

    logging.info('Finished Working on the Training Macbook Chargers worksheet')
    return mac_chargers_list

def thunderbolts(and_items):
    """ return a list of thunderbolts with values: equipment_id, owner_name"""

    # filter and return a list of thunderbolts
    logging.info('Working on the Thunderbolt worksheet')

    # filter_items(and_items, asset_item)
    filtered_list = filter_items(and_items, "Thunderbolt-Ethernet adapter")
    thunderbolts_list = []

    if filtered_list:

        for item in filtered_list:
            col = {
                "equipment_id": item[2] ,
                "owner_name": item[8].strip(),
            }

            thunderbolts_list.append(col)

    logging.info('Finished Working on the Thunderbolts worksheet')
    return thunderbolts_list

def macbooks(sheet_data):
    logging.info('Working on Macbooks')

    # Get and dump mackbooks
    # filter_items(sheet, device_type)
    items = filter_items(sheet_data, "Training Macbook")

    macbook_list = []

    if items:
        for item in items:
            col = {
                "equipment_id": item[2],
                "serial_number": item[6],
                "owner_name": item[8].strip(),
                "owner_cohort": item[9].strip()
            }

            macbook_list.append(col)
    
    logging.info('Finished Working on the Training Macbooks worksheet')
    return macbook_list

def dongles(sheet_data):
    logging.info('Working on Dongles')

    # Get and dump mackbooks
    # filter_items(sheet, device_type)
    items = filter_items(sheet_data, "Dongle")

    dongle_list = []

    if items:
        for item in items:
            col = {
                "equipment_id": item[2] ,
                "owner_name": item[8].strip(),
            }

            dongle_list.append(col)
    
    logging.info('Finished Working on the dongles')
    return dongle_list


def main():
    sheet_name = "Benjamin Copy of Asset Tracker For bot"
    get_all_items(sheet_name)


if __name__ == '__main__':
    main()
