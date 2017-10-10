import requests
import json
from pprint import pprint
import os

headers = {'Authorization': os.getenv('TOKEN')}
res = requests.get(os.getenv('URL'), headers=headers)
all_data = json.loads(res.content)


def get_person_data(all_persons_data):
    """
    Function to
    :param all_persons_data:
    :return:
    """
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
    return persons_data


def location_filter(location, persons_data):
    """
    Function to return all persons whose location is similar
    to the given location

    :param location: The location from which the person should be from
    :param persons_data: Data of all persons
    :return: list of all persons from the given location
    """
    filtered_persons_data = []
    for person in persons_data:
        if person.get("location").lower() == location:
            filtered_persons_data.append(person)
    return filtered_persons_data


data = get_person_data(all_data.get("fellow"))
pprint(data[:5])
pprint(location_filter('nairobi', data)[:5])