import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import pymongo

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
    print "Searching", macbook_data, charger_data, thunderbolt_data
    for records in list_of_dictionaries:
        parsed_data = {records['Andela Code']: records['Fellow Name']}
        search_list.append(parsed_data)
    return search_list

mongodb_client = MongoClient()
db = mongodb_client['saka']

macbooks = db.macbooks
thunderbolts = db.thunderbolts
chargers = db.chargers

macbooks.create_index([('equipment_id', pymongo.TEXT)], unique=True)
chargers.create_index([('equipment_id', pymongo.TEXT)], unique=True)
thunderbolts.create_index([('equipment_id', pymongo.TEXT)], unique=True)

def store_in_db():
    for item in macbook_data:
        macbook = {
        "equipment_id": int(item['Andela Code'].split("/")[-1]),
        "fellow_name": item['Fellow Name'],
        "serial_no": item['Device Serial']
        }
        macbooks.insert_one(macbook)
    print "Inserted macbooks"
    for item in charger_data:
        charger = {
        "equipment_id": int(item['Andela Code'].split("/")[-1]),
        "fellow_name": item['Fellow Name']
        }
        chargers.insert_one(charger)

    print "Inserted chargers"

    for item in thunderbolt_data:
        if item['Andela Code']:
            thunderbolt = {
            "equipment_id": int(item['Andela Code'].split("/")[-1]),
            "fellow_name": item['Fellow Name']
            }
            thunderbolts.insert_one(thunderbolt)

    print "Inserted thunderbolts"

if __name__ == "__main__":
    store_in_db()