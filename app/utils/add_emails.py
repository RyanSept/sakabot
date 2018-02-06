import os
import json
import logging
from fuzzywuzzy import fuzz
from app.utils import gsheet, SPREADSHEET_ID
from app import slack_client, macbooks, chargers, thunderbolts


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


REL_PATH = '/emails.json'
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
EMAILS_FILE = HOME_DIR + REL_PATH
EQUIPMENT_FILE_PATH = HOME_DIR + "/equipment.json"
MATCH_CACHE_FILE_PATH = HOME_DIR + "/match_cache.json"


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
    # loop through equipment db
    for equipment in equipments:
        email = equipment["owner_email"]

        # find row of sheet with equipment_id eg. row with 'AND/TMAC/41'
        row = sheet.find(equipment["equipment_id"]).row
        if row:
            # add email
            sheet.update_cell(row, col, email)


def add_emails_and_slack_id_to_equipment_json():
    """
    Extract slack_id and emails and add them to equipment list
    """
    with open(EQUIPMENT_FILE_PATH, "r") as equipment_file:
        equipment_list = json.loads(equipment_file.read())

    with open(MATCH_CACHE_FILE_PATH, "r") as\
            match_cache_file:
        # slack_ids that user entered manually
        match_cache = match_cache_file.read()
        if match_cache:
            match_cache = json.loads(match_cache)
        else:
            match_cache = {}

    # fetch users list from slack
    slack_response = slack_client.api_call('users.list')
    if not slack_response["ok"]:
        logging.error("Slack raised this error %s", slack_response["error"])

    people_list = slack_response["members"]
    unmatched_equipment_indices = []
    match_count = 0

    for index, item in enumerate(equipment_list["thunderbolts"]):
        if not item["owner_name"]:
            continue

        owner_name = item["owner_name"] = item["owner_name"].strip(" ")

        # check cached manual slack_id entries
        if owner_name in match_cache:
            slack_id = match_cache[owner_name]["owner_slack_id"]
            email = match_cache[owner_name]["owner_email"]
            match_count += 1
            logging.info("Retrieved %s owner details from match cache",
                         item["equipment_id"])
            continue

        # check slack user list for slack_id and email
        logging.debug("Checking slack users.list for owner details.")
        for person in people_list:
            if "email" not in person["profile"]:
                logging.debug(json.dumps(person, indent=4))
                continue
            person_name = person["profile"]["real_name"]
            email = person["profile"]["email"]
            slack_id = person["id"]
            name_from_email = email.split("@")[0]

            # run a fuzzy match of email name and slack real name
            if fuzz.token_sort_ratio(
                person_name.replace("'", ""),
                owner_name.replace("'", "")) >= 100\
                or fuzz.token_sort_ratio(
                    name_from_email,
                    owner_name.replace("'", "")) >= 100:
                logging.info("100 percent match for %s owner details",
                             item["equipment_id"])
                item["owner_email"] = email
                item["owner_slack_id"] = slack_id
                match_cache[owner_name] = {
                    "owner_slack_id": slack_id,
                    "owner_email": email
                }
                match_count += 1
                break

        # if no match was found
        if "owner_email" not in item:
            unmatched_equipment_indices.append(index)

    logging.info("Unmmatched equipment indices: %s",
                 unmatched_equipment_indices)
    logging.info("Matched %s equipment items.", match_count)

    print "We were unable to find matching Slack profiles for {} equipment.".format(
        len(unmatched_equipment_indices))
    print("Please fill in the Slack ids for the following names."
          " If you can't find them on slack or it's not a user"
          " that should be in the system, type 'N'")
    print """
    To get the Slack id of a user:
    1. Open slack and press `cmd + shift + e`
    2. Open the Workspace Directory and find them name.
    3. Click on the result to open their profile
    4. Click 'Copy member ID on the drop down menu'
    """

    # go through unmatched equipment and prompt user for manually input
    # for i in unmatched_equipment_indices:
    #     equipment = equipment_list["thunderbolts"][i]
    #     owner_name = equipment["owner_name"]
    #     while True:
    #         slack_id = raw_input("Enter slack id for {}: ".format(owner_name))
    #         if slack_id == "N" or slack_id == "n":
    #             equipment["unmatched"] = True
    #             break
    #         for person in people_list:
    #             if slack_id == person["id"]: # check a good part of the name matches
    #                 equipment["owner_email"] = email
    #                 equipment["owner_slack_id"] = slack_id
    #                 match_cache[owner_name] = {
    #                     "owner_slack_id": slack_id,
    #                     "owner_email": person["profile"]["email"]
    #                 }
    #                 unmatched_equipment_indices.remove(i)
    #                 print "Successfully matched {}'s equipment".format(
    #                     owner_name)
    #                 break
    #         if "owner_email" in equipment or "unmatched" in equipment:
    #             break

    #     if "owner_email" not in equipment:
    #         print "Unable to find slack_id '{}' on Slack".format(slack_id)
    #         continue


# open equipments.json file
# open manual_slack_id_entries_cache.json file
# fetch users.list from slack
# check if each person in cached manual inputs first then check people_list if so grab their email, slack_id
# if not person in people save that mismatch
# prompt user to manually input mismatch slack_id of person from slack then grab email of those guys (cache user inputs)
# write changes to equipment file


if __name__ == "__main__":
    print "THUNDERBOLTS"
    add_emails_and_slack_id_to_equipment_json()
    # add_emails_to_db(macbooks)
    # print "CHARGERS"
    # add_emails_to_db(chargers)
    # print "THUNDERBOLTS"
    # add_emails_to_db(thunderbolts)

    # add_emails_to_sheet(master_sheet.get_worksheet(0), 6, macbooks.find())
    # add_emails_to_sheet(master_sheet.get_worksheet(1), 4, chargers.find())
    # add_emails_to_sheet(master_sheet.get_worksheet(2), 4, thunderbolts.find())
