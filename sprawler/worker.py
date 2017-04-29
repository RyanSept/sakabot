import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

sheet_list = []
# json credentials you downloaded earlier
rel_path = '/credentials/sakabot-cred.json'
home_dir = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = home_dir + rel_path
SCOPE = ['https://spreadsheets.google.com/feeds']

# get email and key from creds
cred = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE,
                                                        SCOPE)

gsheet = gspread.authorize(cred)  # authenticate with Google
master_sheet = gsheet.open_by_key(
    "1lJ4VUcP1t7kXZNtdVBlfgNDpXVrg--vSlA0iL7H5b4E")  # open sheet

macbook_sheet = master_sheet.get_worksheet(0)
charger_sheet = master_sheet.get_worksheet(1)
thunderbolt_sheet = master_sheet.get_worksheet(2)

macbook_data = macbook_sheet.get_all_records()
charger_data = charger_sheet.get_all_records()
thunderbolt_data = thunderbolt_sheet.get_all_records()

macbook_search_data = []
charger_search_data = []
thunderbolt_search_data = []


def populate_search_data(list_of_dictionaries, search_list):
    for records in list_of_dictionaries:
        parsed_data = {records['Andela Code']: records['Fellow Name']}
        search_list.append(parsed_data)
    return search_list
