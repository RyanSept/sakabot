import os
from pymongo import MongoClient
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Despite db being init in app.init we reinit here to avoid writing to
# prod db. Could be better to have it config based

mongodb_client = MongoClient()
db = mongodb_client['saka']


macbooks = db.macbooks
thunderbolts = db.thunderbolts
chargers = db.chargers


# json credentials you downloaded earlier
REL_PATH = '/credentials/sakabot-cred.json'
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = HOME_DIR + REL_PATH
SPREADSHEET_ID = "19kvSslth-bCy0TaChIAYez1_AT1viIafYwWFwEhXhnA"
SCOPE = ['https://spreadsheets.google.com/feeds',
         "https://www.googleapis.com/auth/spreadsheets "]

# get email and key from creds
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CLIENT_SECRET_FILE,
    SCOPE)
gsheet = gspread.authorize(credentials)  # authenticate with Google
