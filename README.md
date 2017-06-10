# Sakabot
Sakabot is a slackbot designed to help Andelans find the owners of equipment and report them either lost or found. 
It's been built in part using this wrapper to the slack rtm api https://github.com/lins05/slackbot. 

### Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
You'll need a slack api bot token https://api.slack.com/bot-users.

### Installing
Clone the repo from Github by running  `$ git clone git@github.com:RyanSept/sakabot.git`

Change directory into package `$ cd sakabot`

Install the dependencies by running `$ pip install requirements.txt`

You can set the required environment variables like so

```
$ export BOT_TOKEN=<SLACK_API_BOT_TOKEN> 
$ export MONGODB_URI=<URI_TO_MONGO_DATABASE>
$ export ERRORS_TO=<SLACK_USER_TO_SEND_ERRORS_TO>
```

Before running you need to setup the database and populate it by running the sprawler on the OPs spreadsheet with your email credentials
on it. To run the sprawler, you need credentials. To get these, you need to setup a project on the Google Developers Console. 
Follow this guide https://developers.google.com/sheets/api/quickstart/python and copy the credentials file you download 
to app/sprawler/credentials as sakabot-cred.json. Copy the client email value in the credentials file you got and share 
the spreadsheet with that email.

### Deployment
To deploy on heroku, you need to push setup the app on heroku, add the appropriate configs(see installing section), set up a
mongodb and scale the dyno `heroku ps:scale worker=1`

### Usage
*Searching for an item's owner*
To search for an item's owner send `find charger|mac|thunderbolt <item_id>` to _@sakabot_.
eg. `find charger 41`

*Reporting that you've lost an item*
When you lose an item, there's a chance that somebody has found it and submitted it to Sakabot. In that case we'll tell you who found it, otherwise, we'll slack you in case anyone reports they found it. To report an item as lost send `lost charger|mac|thunderbolt <item_id>` to _@sakabot._
eg. `lost thunderbolt 33`

*Submit a found item*
When you find a lost item you can report that you found it and in case a user had reported it lost, we'll slack them immediately telling them you found it. To report that you found an item send `found charger|mac|thunderbolt <item_id>` to _@sakabot_
eg. `found mac 67`
