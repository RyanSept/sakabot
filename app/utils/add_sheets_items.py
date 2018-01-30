from gspread import utils
from operator import itemgetter
from itertools import groupby
import logging
# import the gspread instance
from app.utils import gsheet as gc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# data sheets objects. bot_sheet -> already existing bot data andela_sheet -> Andela equip data sheet
andela_sheet = gc.open("Andela Nairobi Equipments").worksheet("Training Macbooks")


def get_serial_values(sheet, col, col_value, col_num=1):
    """
    Function to return the cell range of asset_code or serial number of an item
    in a sheet.

    Example: Get all cells with asset-code for each thunderbolt

    :param sheet: sheet the tb data is in
    :param col: column which has serial number or asset_code
    :param col_value: The label of the field which says an item is a tb or mac
    :param col_num: column number of the column with the data
    :rtype: list
    :return: serial_nums - list of cell objects in the range
    """
    logging.info('Getting all cells under asset_code column')
    item_cells = []
    and_items = sheet.findall(col_value)
    for item in and_items:
        item_cells.append(item.row)

    # list of lists of consecutive numbers
    cell_lists = [list(map(itemgetter(1), g)) for k, g
                  in groupby(enumerate(item_cells), lambda x: x[0] - x[1])]
    cell_ranges = []
    for cell_list in cell_lists:
        cell_range = '{}{}:{}{}'.format(col, cell_list[0], col, cell_list[-1])
        cell_ranges.extend(sheet.range(cell_range))

    logging.info('{} cells found in sheet {}worksheet'.format(
        len(cell_ranges), sheet.title))

    return cell_ranges


def get_new_items(sheet, bot_col_value, and_col_value, bot_col, and_col):
    """
    Function to return a list of all items not in the bot_sheet
    Example:
        get_new_items('Thunderbolt-Ethernet adapter', 'Thunderbolt-Ethernet adapter', 'A', 'A')

    :param sheet: The bot_sheet to use
    :param bot_col_value: The label of the field which says an item is a tb or mac
            in the bot_sheet e.g 'Thunderbolt-Ethernet adapter'
    :param and_col_value: The label of the field which says an item is a tb or mac
            in the andela_sheet e.g 'Thunderbolt-Ethernet adapter'
    :param bot_col: column which has serial number or asset_code in the bot_sheet
    :param and_col: column which has serial number or asset_code in the andela_sheet
    :return: new_items - list of cell objects of items not in the bot_sheet
            but in the andela_sheet
    """

    # all current item asset-codes or serial numbers in the bot_sheet
    bot_old_items = get_serial_values(sheet, bot_col,
                                      bot_col_value, col_num=1)
    # all current item asset-codes or serial numbers in the andela_sheet
    and_items = get_serial_values(andela_sheet, and_col,
                                  and_col_value, col_num=1)
    bot_items = [item for item in bot_old_items if item.value]
    and_items = [item for item in and_items if item.value]
    # get newly added items, leave them as cell objects - the object data is used in write_data function
    bot_values = [item.value for item in bot_items]
    new_items = [item for item in and_items if item.value not in bot_values]
    logging.info('{} new items found'.format(len(new_items)))
    return new_items


def get_new_items_data(sheet, items, cols, item_label):
    """
    Function to return new item data - item_asset_code and owner from the
    andela_equips sheet which is to be written to the new sheet - bot_sheet
    Example:
        items - from get_new_items() ^^
        get_new_items_data(andela_sheet, items, {"owner_col": 'I'}, "Thunderbolt-Ethernet adapter")
        cols = {"owner_col": 'I'}

    :param sheet: sheet from which the new items are from - andela_sheet
    :param items: new items(cell objects) - tb/tmac/tmac-charger or headsets not in the bot sheet
    :param cols: dict of columns values to be read from andela_sheet
    :param item_label: Value of each cell in the item column e.g 'Thunderbolt-Ethernet adapter'
    :return: items_data - dict with all the new data to be writen to bot_sheet
    """

    items_data = {}
    for item in items:
        # Get the row number which the item is from
        item_row = item.row
        item_owner = sheet.acell('{}{}'.format(cols.get("owner"), item_row)).value

        # check if the item has the owner value if not ignore it.
        # `owner` is a compulsory field for each `cols object`
        if item_owner:
            # Get the other field values for the item - from the above row
            items_data.setdefault(item.value, {})['owner'] = item_owner
            # we already have the owner field value
            for field in [field for field in cols.keys() if field != 'owner']:
                if cols[field]:
                    cell = '{}{}'.format(cols[field], item_row)
                    items_data[item.value][field] = sheet.acell(cell).value
                # Both item and asset_code are available hence no need to get them from sheet
                # item is available as item_label and asset_code as the value of each item
                else:
                    if field == 'item':
                        items_data[item.value][field] = item_label
                    elif field == 'asset_code':
                        items_data[item.value][field] = item.value
                    else:
                        items_data[item.value][field] = ''
        continue
    logging.info('Data from the new items created')
    return items_data


def write_data(sheet, start_row, columns, data, col_len=4):
    # Number of new rows to be writen
    """
    Function to write the newly found data to the bot_sheet
    example columns:
    columns = {
        1: 'item',
        2: 'asset_code',
        3: 'owner'
    }

    :param sheet: Sheet the data is to be written to (bot_sheet)
    :param start_row: The row from which the new data starts to be written
    :param columns: Dict of each col_num with its title as value, check above example
    :param data: The data to be writen to the bot_sheet
    :param col_len: Number of cols in the sheet being writen
    :returns: None
    """
    logging.info('Writing data to {} worksheet'.format(sheet.title))
    rows = len(data.keys())
    # cells to update, assumes, the first column is A - "utils.rowcol_to_a1(start_row, 1)"
    range_start = utils.rowcol_to_a1(start_row, 1)
    range_end = utils.rowcol_to_a1(start_row + rows - 1, col_len)
    cell_list = sheet.range('{}:{}'.format(range_start, range_end))
    # group all cells making up a row into their own list
    row_cels = [list(g) for _, g in groupby(cell_list, lambda cell: cell.row)]

    # update each cell by giving it a value, from the data
    count = 0
    for item in data.keys():
        cells = row_cels[count]
        for cell in cells:
            for col_num in columns.keys():
                if cell.col == col_num:
                    cell.value = data[item].get(columns.get(col_num))
        count += 1

    # un-bundle the row cells
    updated_cells = [cell for row_cell in row_cels for cell in row_cell]
    # update sheet
    sheet.update_cells(updated_cells)
    logging.info('Data written to {} worksheet'.format(sheet.title))


def first_empty_data_row(sheet, col_value, col_num=1):
    """
    Function to return first empty row from the bot_sheet
    Works by checking the 'item' column - will never be empty?!
    Example:
        first_empty_data_row(bot_sheet, "Thunderbolt-Ethernet adapter")

    :param sheet: sheet being checked
    :param col_value: label of the column used to determine empty row
    :param col_num: Which column to use during the check
    :return: first_empty_row - integer
    """
    first_item_row = [cell for cell in sheet.col_values(col_num)].\
        index(col_value) + 1
    bot_items = len([cell for cell in sheet.col_values(col_num)
                    if cell == col_value])
    first_empty_row = bot_items + first_item_row
    logging.info('first empty row of {} worksheet is {}'.format(
        sheet.title, first_empty_row
    ))
    return first_empty_row


def tmac_chargers(sheet):
    logging.info('Working on the Training Macbook Chargers worksheet')
    # Get and write tmac_chargers
    bot_sheet = gc.open(sheet).worksheet("Training Macbook Chargers ")
    # get_new_items(sheet, bot_col_value, and_col_value, bot_col, and_col)
    items = get_new_items(bot_sheet, 'Training Macbook Charger',
                          'Macbook Charger', 'B', 'C')
    cols = {
        "owner": 'I',
        "asset_code": '',
        'item': '',
        'email': ''
    }
    # get_new_items_data(sheet, items, cols, item_label)
    data = get_new_items_data(andela_sheet, items, cols,
                              "Training Macbook Charger")
    columns = {
        1: 'item',
        2: 'asset_code',
        3: 'owner',
        4: 'email'
    }
    # first_empty_data_row(sheet, col_value, col_num=1)
    start_row = first_empty_data_row(bot_sheet, "Training Macbook Charger")
    # write_data(sheet, start_row, columns, data, col_len=4)
    write_data(bot_sheet, start_row, columns, data)
    logging.info('Finished Working on the Training Macbook Chargers worksheet')


def thunderbolts(sheet):
    logging.info('Working on the Thunderbolt worksheet')

    # Get and write thunderbolts
    bot_sheet = gc.open(sheet).worksheet("Thunderbolt ")
    # get_new_items(sheet, bot_col_value, and_col_value, bot_col, and_col)
    items = get_new_items(bot_sheet, 'Thunderbolt-Ethernet adapter',
                          'Thunderbolt-Ethernet adapter', 'B', 'C')
    cols = {
        "owner": 'I',
        "asset_code": '',
        'item': '',
        'email': ''
    }
    # get_new_items_data(sheet, items, cols, item_label)
    data = get_new_items_data(andela_sheet, items, cols,
                              "Thunderbolt-Ethernet adapter")
    columns = {
        1: 'item',
        2: 'asset_code',
        3: 'owner',
        4: 'email'
    }
    # first_empty_data_row(sheet, col_value, col_num=1)
    start_row = first_empty_data_row(bot_sheet,
                                     "Thunderbolt-Ethernet adapter")
    # write_data(sheet, start_row, columns, data, col_len=4)
    write_data(bot_sheet, start_row, columns, data)
    logging.info('Finished Working on the Thunderbolts worksheet')


def headsets(sheet):
    logging.info('Working on the Headsets worksheet')
    # Get and write thunderbolts
    bot_sheet = gc.open(sheet).worksheet("Headsets")
    # get_new_items(sheet, bot_col_value, and_col_value, bot_col, and_col)
    items = get_new_items(bot_sheet, 'Headsets', 'Headsets', 'C', 'C')
    cols = {
        "owner": 'I',
        "description": 'B',
        "asset_code": '',
        'item': ''
    }
    # get_new_items_data(sheet, items, cols, item_label)
    data = get_new_items_data(andela_sheet, items, cols, "Headsets")
    columns = {
        1: 'item',
        2: 'description',
        3: 'asset_code',
        4: 'owner'
    }
    # first_empty_data_row(sheet, col_value, col_num=1)
    start_row = first_empty_data_row(bot_sheet, "Headsets")
    # write_data(sheet, start_row, columns, data, col_len=4)
    write_data(bot_sheet, start_row, columns, data)
    logging.info('Finished Working on the Headsets worksheet')


def tmacs(sheet):
    logging.info('Working on the Training Macbooks worksheet')
    # Get and write thunderbolts
    bot_sheet = gc.open(sheet).worksheet("Training Macbooks ")
    # get_new_items(sheet, bot_col_value, and_col_value, bot_col, and_col)
    items = get_new_items(bot_sheet, 'Training Macbook',
                          'Training Macbook', 'C', 'C')
    cols = {
        "owner": 'I',
        "description": 'B',
        "serial": 'G',
        "asset_code": '',
        "cohort": 'J',
        'item': '',
        'email': ''
    }
    # get_new_items_data(sheet, items, cols, item_label)
    data = get_new_items_data(andela_sheet, items, cols, 'Training Macbook')
    columns = {
        1: 'item',
        2: 'description',
        3: 'asset_code',
        4: 'serial',
        5: 'owner',
        6: 'email',
        7: 'cohort'
    }
    # first_empty_data_row(sheet, col_value, col_num=1)
    start_row = first_empty_data_row(bot_sheet, 'Training Macbook')
    # write_data(sheet, start_row, columns, data, col_len=4)
    write_data(bot_sheet, start_row, columns, data, col_len=7)
    logging.info('Finished Working on the Training Macbooks worksheet')


def main():
    sheet_name = "Ryan Copy of Andela Nairobi Equipments"
    thunderbolts(sheet_name)
    tmac_chargers(sheet_name)
    tmacs(sheet_name)


if __name__ == '__main__':
    main()
