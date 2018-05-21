"""
This script is to be called after get_equipment_from_sheet.py.
It solves the problem of identifying an equipment owner. Our user details
database is slack. Equipment owner names in the equipment store are
 unstandardized (a different name is used in the sheet from the one on slack)
or may contain errors. Our first approach is to try finding a slack user by the
given name. If that works out we celebrate the match and cache that,
 otherwise we store that and at the end of the matching process, we ask for
manual entry of the user info. These manual entries are also added to the
 owner details cache for reuse. This cache contains the unstandardized user
 name (as they are in the spreadsheet) as the key and slack user details as the
 value.
"""
import os
import json
import logging
from app import slack_client
from fuzzywuzzy import fuzz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


REL_PATH = '/emails.json'
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
EMAILS_FILE = HOME_DIR + REL_PATH
EQUIPMENT_FILE_PATH = HOME_DIR + "/equipment.json"
OWNER_DETAILS_CACHE_FILE_PATH = HOME_DIR + "/name_to_owner_details_cache.json"


def add_emails_and_slack_id_to_equipment_json(equipment_list, owner_details_cache, people_list):
    """
    Add slack_id and email to each equipment item

    :param equipment_list: list of equipment eg. list of macbooks
    :param owner_details_cache: cache of names that have been matched to slack details
    :param people_list: list of slack users
    :return: tuple containing equipment_list and owner_details_cache
    """
    unmatched_equipment_indices = []
    match_count = 0

    for index, item in enumerate(equipment_list):
        if not item["owner_name"]:
            continue

        owner_name = item["owner_name"] = item["owner_name"].strip(" ")

        # check cached owner_details
        if owner_name in owner_details_cache:
            slack_id = owner_details_cache[owner_name]["owner_slack_id"]
            email = owner_details_cache[owner_name]["owner_email"]
            item["owner_email"] = email
            item["owner_slack_id"] = slack_id
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

                # add to cache
                owner_details_cache[owner_name] = {
                    "owner_slack_id": slack_id,
                    "owner_email": email
                }
                match_count += 1
                break

        # if no match was found
        if "owner_email" not in item:
            unmatched_equipment_indices.append(index)

    logging.info("Matched %s equipment items.", match_count)

    if len(unmatched_equipment_indices) == 0:
        return equipment_list, owner_details_cache

    logging.info("Unmmatched equipment indices: %s",
                 unmatched_equipment_indices)
    """
    Requst manual slack id entries for equipment that we were'nt able to
    find owner details automatically
    """
    print("We were unable to find matching Slack profiles for {} equipment.".format(
        len(unmatched_equipment_indices)))
    print("Please fill in the Slack ids for the following names."
          " If you can't find them on slack or it's not a user"
          " that should be in the system, type 'N'")
    print("""
    To get the Slack id of a user:
    1. Open slack and press `cmd + shift + e`
    2. Open the Workspace Directory and find them name.
    3. Click on the result to open their profile
    4. Click 'Copy member ID on the drop down menu'
    """)

    # go through unmatched equipment and prompt user to manually input for each
    dont_match_list = []
    for i in unmatched_equipment_indices:
        equipment = equipment_list[i]
        owner_name = equipment["owner_name"]

        # ignore equipment with these names
        if owner_name in []:
            equipment["unmatched"] = True
            dont_match_list.append(equipment)
            continue

        # get user input for slack_id of owner of the equipment
        while True:
            slack_id = input("Enter slack id for {}: ".format(owner_name))
            if slack_id == "N" or slack_id == "n":
                equipment["unmatched"] = True
                dont_match_list.append(equipment)
                break
            for person in people_list:
                if slack_id == person["id"]:
                    equipment["owner_email"] = email
                    equipment["owner_slack_id"] = slack_id
                    owner_details_cache[owner_name] = {
                        "owner_slack_id": slack_id,
                        "owner_email": person["profile"]["email"]
                    }
                    print("Successfully matched {}'s equipment".format(
                        owner_name))
                    break
            else:
                print("Unable to find slack_id '{}' on Slack".format(slack_id))

            if "owner_email" in equipment:
                break

    # remove rejects
    for equipment in dont_match_list:
        equipment_list.remove(equipment)

    return equipment_list, owner_details_cache


if __name__ == "__main__":
    # fetch users list from slack
    slack_response = slack_client.api_call('users.list')
    if not slack_response["ok"]:
        logging.error("Slack raised this error %s", slack_response["error"])

    people_list = slack_response["members"]
    with open(EQUIPMENT_FILE_PATH, "r") as equipment_file:
        equipment_data = json.loads(equipment_file.read())

    with open(OWNER_DETAILS_CACHE_FILE_PATH, "r") as owner_details_cache_file:
        # slack_ids that user entered manually
        owner_details_cache = owner_details_cache_file.read()
        if owner_details_cache:
            owner_details_cache = json.loads(owner_details_cache)
        else:
            owner_details_cache = {}

    for equipment_type in equipment_data:
        print(equipment_type)
        result = add_emails_and_slack_id_to_equipment_json(
            equipment_data[equipment_type], owner_details_cache,
            people_list)
        equipment_data[equipment_type] = result[0]
        owner_details_cache = result[1]

    with open(EQUIPMENT_FILE_PATH, "w+") as equipment_file:
        equipment_file.write(json.dumps(equipment_data))

    with open(OWNER_DETAILS_CACHE_FILE_PATH, "w+") as owner_details_cache_file:
        owner_details_cache_file.write(json.dumps(owner_details_cache))
