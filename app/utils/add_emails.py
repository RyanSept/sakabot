import os
import json
from fuzzywuzzy import fuzz
from app.utils import gsheet, SPREADSHEET_ID
from app import macbooks, chargers, thunderbolts

REL_PATH = '/emails.json'
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
EMAILS_FILE = HOME_DIR + REL_PATH


class Match():
    '''
    Best email match class
    Inits with score, a levenshtein distance and email, the string with that
    distancce
    '''

    def __init__(self, diff, email=None):
        self.diff = diff
        self.email = email

    def __repr__(self):
        return "<email:{} | diff: {}>".format(self.email, self.diff)


def add_emails_to_db(collection):
    '''
    Add emails to equipment data in database
    '''
    equipments = collection.find()
    with open(EMAILS_FILE, "r") as emails_file:
        emails = emails_file.read()
        emails = json.loads(emails)["results"]

    # list of matches that weren't exact
    not_exact_match = []
    # because macbooks isn't a list we have num_macs.
    num_macs = count = 0
    for equipment in equipments:
        num_macs += 1
        # match object with initial diff
        match = Match(-1)
        for email in emails:
            name = email["Andela Email"].split("@")[0]
            diff = fuzz.token_sort_ratio(
                equipment["owner_name"].replace("'", ""), name)
            if diff > match.diff:
                match.email = email["Andela Email"].strip()
                match.diff = diff
            if diff == 100:
                count += 1
                break
        if match.diff != 100:
            not_exact_match.append(
                (match.email, equipment["owner_name"], match.diff))
        collection.update_one(
            equipment, {"$set": {"owner_email": match.email}})
        equipment["owner_email"] = match.email
        # print match.email, equipment["owner_name"], match.diff
    print "Num equipment: " + str(num_macs)
    print "100% matches: " + str(count)
    print "Non-exact matches: {}".format(len(not_exact_match)), not_exact_match


master_sheet = gsheet.open_by_key(SPREADSHEET_ID)  # open sheet


def add_emails_to_sheet(sheet, col, equipments):
    '''
    Add emails to spreadsheet
    Takes the sheet and the column to add the emails to
    '''
    # loop through equipment
    for equipment in equipments:
        email = equipment["owner_email"]

        # find row of sheet with equipment_id eg. row with 'AND/TMAC/41'
        row = sheet.find(equipment["equipment_id"]).row
        if row:
            # add email
            sheet.update_cell(row, col, email)


if __name__ == "__main__":
    print "MACBOOKS"
    add_emails_to_db(macbooks)
    print "CHARGERS"
    add_emails_to_db(chargers)
    print "THUNDERBOLTS"
    add_emails_to_db(thunderbolts)
    add_emails_to_sheet(master_sheet.get_worksheet(0),
                        6, macbooks.find())

    add_emails_to_sheet(master_sheet.get_worksheet(1), 4, chargers.find())
    add_emails_to_sheet(master_sheet.get_worksheet(2), 4, thunderbolts.find())
