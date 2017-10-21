import requests
import json
import os
import logging

from app import slack_client

# setup info logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


def fix_null_name(people):
    """
    Function to fix null values for both first_name and last_name
    if real_name field exists and is made up of two names
    :param people: list of person data objects
    :return: people - modified list of person data objects
    """

    logging.info('Fixing null name values')
    count = 0
    for person in people:
        if not (person.get('first_name') and person.get('last_name')):
            real_name = person.get('real_name')
            if len(real_name.split()) == 2:
                first, last = real_name.split()
                people[count]['first_name'] = first
                people[count]['last_name'] = last
                logging.info('Fixed {}\'s null name values'.format(real_name))
        count += 1
    return people


def get_data(url, params):
    """
    Function to download data
    :param params: dict of query strings for the url
    :param url: url
    :return: data - json data gotten
    """
    logging.info('Requesting for the data...')
    if url:
        res = slack_client.api_call(url, **params)
        data = json.loads(res)
        if data.get('ok'):
            logging.info('Finished downloading data')
            return data
        else:
            msg = data.get('error')
            raise Exception(msg)
    else:
        msg = 'URL cannot be None'
        raise requests.exceptions.MissingSchema(msg)


def get_people_data(person_ids, all_persons_data):
    """
    Function to get selected info from each person object

    :param person_ids: List of ids of persons whose data we need
    :param all_persons_data: list of person data objects
    :return: persons_data - list of selected person data objects
    """
    logging.info('Selecting Names and email only from the downloaded data')
    persons_data = []
    for person_obj in all_persons_data:
        if person_obj.get('id') in person_ids:
            person_details = person_obj.get("profile")
            # catch bots since they got no email
            email = person_details.get('email')
            if email:
                selected_data = {
                    'first_name': person_details.get('first_name'),
                    'last_name': person_details.get('last_name'),
                    'real_name': person_details.get('real_name'),
                    'email': email
                }
                persons_data.append(selected_data)
    logging.info('Selected data for {} People'.format(len(persons_data)))
    return persons_data


def get_peoples_id(group_data):
    """
    Function to return all persons whose location is similar
    to the given location

    :param group_data: Data of all persons
    :return: persons_id - list of all group members
    """
    logging.info('Getting persons IDs')
    persons_id = group_data.get('members')
    logging.info('{} IDs found'.format(len(persons_id)))
    return persons_id


def write_to_file(persons_data, filename):
    """
    Function to write json data to file
    :param persons_data: json data to be writen to file
    :param filename: Name of the file the data is to be written to
    """
    logging.info('Starting to write the selected data to emails.json')
    with open(filename, 'w') as f:
        # ensure_ascii makes sure that all ascii characters are left untouched
        json.dump(persons_data, f, ensure_ascii=False, indent=4)
    logging.info('File writen --> Done')


def request_people_data():
    """
    Function to get raw people data
    :rtype: tuple
    :return: tuple - raw_staff and raw_fellow data
    """
    # channel_id for channel with all people in a certain location
    channel_id = os.getenv('CHANNEL_ID')
    # url for group.info endpoint
    group_url = 'groups.info'
    # url for users.list endpoint
    channel_url = 'users.list'
    # extra params here
    group_params = {'channel': channel_id}
    try:
        raw_group_data = get_data(group_url, group_params)
        # no params since - {}
        raw_channel_data = get_data(channel_url, {})
        return raw_group_data, raw_channel_data
    except requests.exceptions.MissingSchema as err:
        logging.error('Error --> {}'.format(err))
    except Exception as err:
        if 'not_authed' in err.args:
            msg = 'Invalid or missing Token'
            logging.error('Error --> {}'.format(msg))
        elif 'channel_not_found' in err.args:
            msg = 'channel_not_found: Missing or invalid CHANNEL_ID'
            logging.error('Error --> {}'.format(msg))
        else:
            logging.error('Error --> {}'.format(err))


if __name__ == '__main__':
    # NOTE: This file requires channel_id to run
    # these variable should be set as env variables as CHANNEL_ID

    try:
        group_ids, channel_members = request_people_data()
        ids = get_peoples_id(group_ids.get('group'))
        all_people_data = get_people_data(ids, channel_members.get('members'))
        # fix null values for first and last name
        people_data = fix_null_name(all_people_data)
        write_to_file(people_data, 'emails.json')
    except TypeError:
        # catch TypeError when request_people_data fails
        pass
