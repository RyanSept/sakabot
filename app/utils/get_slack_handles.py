from app import slack_client, slack_handles


def fetch_all_slack_handles():
    '''
    Fetch all ids of everyone on slack
    Return a dictionary with the email as the key and the slack id as the value
    '''
    users = slack_client.api_call('users.list')["members"]
    formatted_users_list = {}
    for user in users:
        if "email" in user["profile"]:
            email = user["profile"]["email"]
            formatted_users_list[email] = user["id"]

    return formatted_users_list


slack_ids = fetch_all_slack_handles()


def get_slack_handles(collection):
    '''
    Get slack handles using email from slack and store in db
    '''
    for equipment in collection:
        email = equipment["owner_email"]
        # if the slack handle associated with that email isn't
        # in the collection
        if email and not slack_handles.find({"email": email}).count():
            # check that the owner email is in the collection
            if email in slack_ids:
                slack_handles.insert_one(
                    {"email": email,
                     "slack_id": slack_ids[email]
                     })
            else:
                print "Is {} a non-Andelan? They're not on slack".format(email)
