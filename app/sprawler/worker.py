from app.sprawler import gsheet, SPREADSHEET_ID
from app import macbooks, chargers, thunderbolts


def retrieve_data_from_spreadsheet():
    master_sheet = gsheet.open_by_key(SPREADSHEET_ID)  # open sheet

    # get respective sheets
    macbook_sheet = master_sheet.get_worksheet(0)
    charger_sheet = master_sheet.get_worksheet(1)
    thunderbolt_sheet = master_sheet.get_worksheet(2)

    # take the relevant rows from each sheet
    macbook_data = macbook_sheet.range("C4:F" + str(macbook_sheet.row_count))
    charger_data = charger_sheet.range("B4:D" + str(charger_sheet.row_count))
    thunderbolt_data = thunderbolt_sheet.range("B4:D" + str(
        thunderbolt_sheet.row_count
    ))

    return {
        "macbook": format_data(macbook_data, "macbook"),
        "charger": format_data(charger_data, "charger"),
        "thunderbolt": format_data(thunderbolt_data, "thunderbolt")
    }


def format_data(sheet_data, sheet_name):
    '''
    Format the data gotten from the spreadsheet to json
    '''
    # number of columns of data we got from each sheet
    chunks = {"macbook": 4, "charger": 3, "thunderbolt": 3}
    new_data = []
    if sheet_name not in chunks:
        raise ValueError
        return

    # sheet data is not grouped into rows so we group them into rows
    # then build the json objects
    for indx in xrange(0, len(sheet_data), chunks[sheet_name]):
        #  chunks[sheet_name] is the size of a row / differing for each sheet
        row = sheet_data[indx:indx + chunks[sheet_name]]

        # if the column with equipment_id is empty go to the next item in list
        if not row[0].value:
            continue

        if sheet_name == "macbook":
            equipment = {
                "equipment_id": int(row[0].value.strip().split("/")[-1]),
                "serial_no": row[1].value,
                "owner_name": row[2].value.strip(),
                "owner_email": row[3].value.strip()
            }
        else:
            equipment = {
                "equipment_id": int(row[0].value.strip().split("/")[-1]),
                "owner_name": row[1].value.strip(),
                "owner_email": row[2].value.strip()
            }

        new_data.append(equipment)

    return new_data


def store_in_db(collection_name, data):
    '''
    Store data in specified db
    '''
    collections = {
        "macbook": macbooks,
        "charger": chargers,
        "thunderbolt": thunderbolts
    }
    if collection_name not in collections:
        raise ValueError
        return

    collection = collections[collection_name]
    # drop that db down low
    collection.drop()
    collection.insert_many(data)
    print "Inserted {}".format(collection)


if __name__ == "__main__":
    data = retrieve_data_from_spreadsheet()
    for key in data:
        print data[key]
        store_in_db(key, data[key])
    print "Om nom nom nom..."
