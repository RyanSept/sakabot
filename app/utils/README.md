# THE APP.UTILS MODULE
This module is like a bad joke. It needs a whole lot of explaining. It contains:

    1. ETL scripts for equipment data - get_equipment_from_sheet.py ad match_equipment_to_owner.py
    2. The fortunes.json file which contains quippy loading messages


## USAGE
To extract the equipment data from the asset spreadsheet run 

`$ python -m app.utils.get_equipment_from_sheet`

To match equipment to owners, run:

`$ python -m app.utils.match_equipment_to_owner`

To run both of them at once:
`$ python -m app.utils.get_equipment_from_sheet && python -m app.utils.match_equipment_to_owner`



## get_equipment_from_sheet.py
This script fetches tmacs, thunderbolts, dongles and chargers from the asset
spreadsheet and writes them to the equipment.json file. It dumps unmatched 
equipment i.e equipment that's yet to be matched to owner details such as
email and slack id. The next script to call after this one is the
match_equipment_to_owner.py script which should add the owner details from
slack. The equipment.json looks like this:

```
    {
        macbooks: [ {
            "equipment_id": "",
            "owner_name": "",
            "serial_number": "",
            "owner_cohort": ""}
            ... 
            ],
        thunderbolts: [ {
            "equipment_id": "",
            "owner_name": ""}
             ... 
             ],
        chargers: [ {
            "equipment_id": "",
            "owner_name": ""} 
            ...
            ],
        dongles: [ {
            "equipment_id": "",
            "owner_name": ""}
            ... 
        ]
    }
```

## match_equipment_to_owner.py
This script is to be called after get_equipment_from_sheet.py.
It solves the problem of identifying an equipment owner.
The problem is equipment owner names in the spreadsheet are
 unstandardized (a different name is used in the sheet from the one on slack or other user dbs)
or may contain errors. We use Slack as a database to get standardized names. 

Our first approach is to try finding a slack user by the
given name. If that works out we celebrate the match and cache that,
 otherwise we note that and at the end of the matching process, we ask for
manual entry of the user info for unsuccessful automatic matches. These manual entries are also added to the
 owner details cache for reuse. This cache is a mapping of the unstandardized user
 name (as they are in the spreadsheet) to slack user details. It is saved in the file 
 `name_to_owner_details_cache.json` which is gitignored.

 Subsequent runs of the match_equipment_to_owner script try reading through the cache first to get owner slack details.


This script transforms the equipment.json to the following format:

```
    {
        macbooks: [ {
            "equipment_id": /* remains untransformed */, 
            "serial_number": /* remains untransformed */, 
            "owner_name": /* remains untransformed */,
            "owner_cohort": /* remains untransformed */, 
            "owner_email": "",
            "owner_slack_id": ""
            } 
        ],
        thunderbolts: [ {
            "equipment_id": /* remains untransformed */,
            "owner_name": /* remains untransformed */,
            "owner_email": "",
            "owner_slack_id": ""
            }
        ],
        chargers: [ {
            "equipment_id": /* remains untransformed */,
            "owner_name": /* remains untransformed */,
            "owner_email": "",
            "owner_slack_id": ""
            }
        ],
        dongles: [ {
            "equipment_id": /* remains untransformed */,
            "owner_name": /* remains untransformed */,
            "owner_email": "",
            "owner_slack_id": ""
            }
        ]
    }

NB: Remains untransformed means it's left exactly as it was in the asset spreadsheet.
```

The spreadsheet name to slack details cache looks like this:

```
{ { "owner_name_as_in_spreadsheet": {"owner_email": "", "owner_slack_id": ""} ... }
```

