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


def get_tb_values(sheet, col, col_num=1):
    """
    Function to return the cell range of asset_code of all TBs in the given sheet

    :param col_num: column number of the column with the data
    :rtype: list
    :param sheet: sheet the tb data is in
    :param col: column which has tb asset_code
    :return: tb_codes - list of cell objects in the range
    """

    and_tbs = len([cell for cell in sheet.col_values(col_num)
                   if cell == "Thunderbolt-Ethernet adapter"])

    first_tb_row = [cell for cell in sheet.col_values(col_num)].\
        index("Thunderbolt-Ethernet adapter") + 1
    tb_asset_cell_range = f'{col}{first_tb_row}:{col}{and_tbs + first_tb_row - 1}'
    tb_codes = sheet.range(tb_asset_cell_range)
    return tb_codes


def check_for_new_tb():
    """
    Function to return a list of all TBs not in the bot_sheet

    :return: new_tbs - list of tb_asset_codes
    """

    # all current thunderbolts asset-codes in the bot_sheet
    bot_tbs = [tb for tb in get_tb_values(bot_sheet, 'B') if tb.value]
    andela_tbs = [tb for tb in get_tb_values(andela_sheet, 'C') if tb.value]
    # get newly added tbs
    new_tbs = [tb for tb in andela_tbs if tb.value and tb.value not in
               [tb.value for tb in bot_tbs]]
    return new_tbs


def get_new_tb_data(sheet, tbs, cols):
    """
    Function to return new tb data - tb_asset_code and owner from the
    andela_equips sheet which s to be written to the new sheet - bot_sheet

    :param sheet: sheet from which the new tbs are from - andela_sheet
    :param tbs: new thunderbolts not in the bot sheet
    :param cols: dict of columns of values to be read from andela_sheet
    :return: tb_data - dict with all the new data to be writen to bot_sheet
    """
    tb_data = {}
    for tb in tbs:
        tb_row = re.findall(r'\d+', utils.rowcol_to_a1(tb.row, tb.col))[0]
        tb_owner = sheet.acell(f'{cols.get("owner_col")}{tb_row}')
        tb_data[tb.value] = {
            'owner': tb_owner.value,
            'item': 'Thunderbolt-Ethernet adapter',
            'asset_code': tb.value
        }

    return tb_data


def write_data(sheet, start_row, cols, data):
    rows = len(data.keys())
    columns = 4
    # cells to update
    cell_list = sheet.range(f'{utils.rowcol_to_a1(start_row, 1)}:'
                            f'{utils.rowcol_to_a1(start_row+rows - 1, columns)}')
    # group all cells making up a row into their own list
    row_cells = [list(g) for _, g in itertools.groupby(cell_list, lambda cell: cell.row)]

    # update each cell by giving it a value
    count = 0
    for tb in data.keys():
        cells = row_cells[count]
        for cell in cells:
            if cell.col == 1:
                cell.value = data[tb].get('item')
            elif cell.col == 2:
                cell.value = data[tb].get('asset_code')
            elif cell.col == 3:
                cell.value = data[tb].get('owner')
            else:
                cell.value = ''
        count += 1
    # un-bundle the row cells
    updated_cells = [cell for row_cell in row_cells for cell in row_cell]
    # update sheet
    sheet.update_cells(updated_cells)
    print('Sheet update -- Hooray')


def first_empty_data_row(sheet, col_num=1):
    """
    Function to return first empty row from the bot_sheet
    :param sheet: sheet being checked
    :param col_num: Which column to use during the check
    :return: first_empty_row - integer
    """
    first_tb_row = [cell for cell in sheet.col_values(col_num)].\
        index("Thunderbolt-Ethernet adapter") + 1
    bot_tbs = len([cell for cell in sheet.col_values(col_num)
                   if cell == "Thunderbolt-Ethernet adapter"])
    first_empty_row = bot_tbs + first_tb_row
    return first_empty_row


data = get_new_tb_data(andela_sheet, check_for_new_tb(), {"owner_col": 'I'})
print(write_data(bot_sheet, first_empty_data_row(bot_sheet), 4, data))
