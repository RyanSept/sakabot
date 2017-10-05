import gspread
from gspread import utils
from oauth2client.service_account import ServiceAccountCredentials
import re
import itertools


scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('pySheet-ef14783798de.json', scope)
gc = gspread.authorize(credentials)

# data sheets objects. bot_sheet -> already existing bot data andela_sheet -> Andela equip data sheet
bot_sheet = gc.open("Gathu Copy of Andela Nairobi Equipments").worksheet("Thunderbolt ")
andela_sheet = gc.open("Gathu Copy of Asset Tracker For bot").worksheet("Master  Inventory List")


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

    and_items = len([cell for cell in sheet.col_values(col_num)
                    if cell == col_value])

    first_item_row = [cell for cell in sheet.col_values(col_num)].\
        index(col_value) + 1
    item_cell_range = f'{col}{first_item_row}:' \
                      f'{col}{and_items + first_item_row - 1}'
    item_cells = sheet.range(item_cell_range)
    return item_cells


def get_new_items(bot_col_value, and_col_value, bot_col, and_col):
    """
    Function to return a list of all items not in the bot_sheet
    Example:
        get_new_items('Thunderbolt-Ethernet adapter', 'Thunderbolt-Ethernet adapter', 1, 1)

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
    bot_old_items = get_serial_values(bot_sheet, bot_col, bot_col_value, col_num=1)
    # all current item asset-codes or serial numbers in the andela_sheet
    and_items = get_serial_values(andela_sheet, and_col, and_col_value, col_num=1)

    bot_items = [item for item in bot_old_items if item.value]
    andela_items = [item for item in and_items if item.value]
    # get newly added items
    new_items = [item for item in andela_items if item.value and item.value not in
               [item.value for item in bot_items]]
    return new_items


def get_new_items_data(sheet, items, cols, item_label):
    """
    Function to return new item data - item_asset_code and owner from the
    andela_equips sheet which is to be written to the new sheet - bot_sheet
    Example:
        items - from get_new_items() ^^
        get_new_items_data(andela_sheet, items, {"owner_col": 'I'}, "Thunderbolt-Ethernet adapter")

    :param sheet: sheet from which the new items are from - andela_sheet
    :param items: new items - tb/tmac/tmac-charger or headsets not in the bot sheet
    :param cols: dict of columns values to be read from andela_sheet
    :param item_label: Value of each cell in the item column e.g 'Thunderbolt-Ethernet adapter'
    :return: items_data - dict with all the new data to be writen to bot_sheet
    """
    items_data = {}
    for item in items:
        # Get the row number which the tb is from
        item_row = re.findall(r'\d+', utils.rowcol_to_a1(item.row, item.col))[0]
        # Get the tb owner value from the above row
        item_owner = sheet.acell(f'{cols.get("owner_col")}{item_row}')

        # check if the item has the owner value if not ignore it.
        if item_owner.strip():
            # TODO: Change this to be done dynamically - since number of fields to be saved differ! - use cols variable
            items_data[item.value] = {
                'owner': item_owner.value,
                'item': item_label,
                'asset_code': item.value
            }
        else:
            continue

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
    rows = len(data.keys())
    # cells to update, assumes, the first column is A - "utils.rowcol_to_a1(start_row, 1)"
    cell_list = sheet.range(f'{utils.rowcol_to_a1(start_row, 1)}:'
                            f'{utils.rowcol_to_a1(start_row + rows - 1, col_len)}')
    # group all cells making up a row into their own list
    row_cells = [list(g) for _, g in itertools.groupby(cell_list,
                                                       lambda cell: cell.row)]

    # update each cell by giving it a value, from the data
    count = 0
    for item in data.keys():
        cells = row_cells[count]
        for cell in cells:
            for col_num in columns.keys():
                if cell.col == col_num:
                    cell.value = data[item].get(columns.get(col_num))
        count += 1

    # un-bundle the row cells
    updated_cells = [cell for row_cell in row_cells for cell in row_cell]
    # update sheet
    sheet.update_cells(updated_cells)
    print('Sheet update successful -- Hooray')


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
    return first_empty_row


items = get_new_items('Thunderbolt-Ethernet adapter', 'Thunderbolt-Ethernet adapter', 1, 1)
data = get_new_items_data(andela_sheet, items, {"owner_col": 'I'}, "Thunderbolt-Ethernet adapter")
columns = {
    1: 'item',
    2: 'asset_code',
    3: 'owner'
}
print(write_data(bot_sheet, first_empty_data_row(bot_sheet, "Thunderbolt-Ethernet adapter"), columns, data))
