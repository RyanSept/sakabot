import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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
