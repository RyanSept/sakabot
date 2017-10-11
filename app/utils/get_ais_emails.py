import requests
import json
import os


def get_ais_data():
    """
    Function to get people data from ais
    :return: all_data - json data gotten
    """
    token = os.getenv('TOKEN')
    url = os.getenv('URL')
    if url:
        headers = {'Authorization': token}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            all_data = json.loads(res.content)
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


def write_to_file(persons_data, filename):
    """
    Function to write json data to file
    :param persons_data: json data to be writen to file
    :param filename: Name of the file the data is to be written to
    """
    with open(filename, 'w') as f:
        # ensure_ascii makes sure that all ascii characters are left untouched
        json.dump(persons_data,  f, ensure_ascii=False, indent=4)
    return 'File writen --> Done'


if __name__ == '__main__':
    # get ais data
    try:
        ais_data = get_ais_data()
        # select first, last and email fields
        data = get_person_data(ais_data.get("fellow"))
        # filter for location
        nairobi_people = location_filter('nairobi', data)
        # write filtered data to file
        print(write_to_file(nairobi_people, 'emails.json'))
    except requests.exceptions.MissingSchema as err:
        print('Error -->', err)
    except Exception as err:
        print('Error -->', err)
