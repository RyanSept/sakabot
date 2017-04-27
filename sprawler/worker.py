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
sheet_list.extend([macbook_sheet, charger_sheet, thunderbolt_sheet])

for sheet in sheet_list:
    selected_cells = sheet.range('C1:C8')
    print(selected_cells)
