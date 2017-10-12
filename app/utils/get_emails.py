import requests
import json
import os
import logging

# setup info logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


def get_data():
    """
    Function to download people data
    :return: all_data - json data gotten
    """
    logging.info('Requesting for the data...')
    token = os.getenv('TOKEN')
    url = os.getenv('URL')
    if url:
        headers = {'Authorization': token}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            all_data = json.loads(res.content)
            logging.info('Finished downloading data')
            return all_data
        else:
            msg = 'Invalid token or Site down'
            raise Exception(msg)
    else:
        msg = 'URL cannot be None'
        raise requests.exceptions.MissingSchema(msg)


def get_person_data(all_persons_data):
    """
    Function to get selected info from each person object
    :param all_persons_data:
    :return: persons_data - list of selected person data objects
    """
    logging.info('Selecting Names and email only from the downloaded data')
    persons_data = []
    for person_obj in all_persons_data:
        person_details = person_obj.get("personal_details")
        names = person_details.get("name").split()
        selected_data = {
            "first_name": names[0],
            "last_name": names[-1],
            "email": person_details.get("email"),
            "location": person_details.get("location")
        }
        persons_data.append(selected_data)
    logging.info('Selected data for {} People'.format(len(persons_data)))
    return persons_data


def location_filter(location, persons_data):
    """
    Function to return all persons whose location is similar
    to the given location

    :param location: The location from which the person should be from
    :param persons_data: Data of all persons
    :return: list of all persons from the given location
    """
    logging.info('Starting to filter selected data'
                 ' by given location: {}'.format(location.capitalize()))
    filtered_persons_data = []
    for person in persons_data:
        if person.get("location").lower() == location:
            filtered_persons_data.append(person)
    filtered_data = len(filtered_persons_data)
    logging.info('{} people from {} found'.format(filtered_data,
                                                  location.capitalize()))
    return filtered_persons_data


def write_to_file(persons_data, filename):
    """
    Function to write json data to file
    :param persons_data: json data to be writen to file
    :param filename: Name of the file the data is to be written to
    """
    logging.info('Starting to write the filtered data to emails.json')
    with open(filename, 'w') as f:
        # ensure_ascii makes sure that all ascii characters are left untouched
        json.dump(persons_data, f, ensure_ascii=False, indent=4)
    logging.info('File writen --> Done')


if __name__ == '__main__':
    # get ais data
    try:
        people_data = get_data()
        # select first, last and email fields
        data = get_person_data(people_data.get("fellow"))
        # filter for location
        nairobi_people = location_filter('nairobi', data)
        # write filtered data to file
        write_to_file(nairobi_people, 'emails.json')
    except requests.exceptions.MissingSchema as err:
        logging.error('Error --> {}'.format(err))
    except Exception as err:
        logging.error('Error --> {}'.format(err))
