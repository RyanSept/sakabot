import gspread
from oauth2client.service_account import ServiceAccountCredentials


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

    and_tbs = len([cell for cell in sheet.col_values(col_num) if cell == "Thunderbolt-Ethernet adapter"])
    # +1 to cater for zero-based index
    first_tb_row = [cell for cell in sheet.col_values(col_num)].index("Thunderbolt-Ethernet adapter")
    tb_asset_cell_range = f'{col}{first_tb_row}:{col}{and_tbs + first_tb_row}'
    tb_codes = sheet.range(tb_asset_cell_range)
    return tb_codes


def check_for_new_tb():
    """
    Function to return a list of all TBs not in the bot_sheet
    :return: new_tbs - list of tb_asset_codes
    """

    # all current thunderbolts asset-codes in the bot_sheet
    bot_tbs = [tb.value for tb in get_tb_values(bot_sheet, 'B') if tb.value]
    andela_tbs = [tb.value for tb in get_tb_values(andela_sheet, 'C') if tb.value]
    # get newly added tbs
    new_tbs = [tb for tb in andela_tbs if tb not in bot_tbs]
    return new_tbs


