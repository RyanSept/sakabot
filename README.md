# Sakabot
Sakabot is a slackbot designed to help Andelans find the owners of equipment. It is built off of Slack's Events API.

### Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
Python 3.6.x
See ENV configs section.

### Installing
Clone the repo from Github by running  `$ git clone git@github.com:RyanSept/sakabot.git`

Change directory into package `$ cd sakabot`

Install the dependencies by running `$ pip install requirements.txt`

You can set the required environment variables like so

```
$ export BOT_TOKEN=<SLACK_API_BOT_TOKEN> 
$ export SLACK_VERIFICATION_TOKEN=<TOKEN_FOR_VERIFYING_EVENTS_SLACK_SENDS>
$ export ASSET_SPREADSHEET_KEY=<SPREADSHEET_ID_FOR_ASSET_SHEET>
$ export ADMIN_SLACK_ID=<USER_ID_OF_ADMIN>  # not necessary in dev stage
```

Before running you need to setup the datastore and populate it by running the extractor on the OPs spreadsheet with your email credentials
on it. To run the extractor, you need credentials. To get these, you need to setup a project on the Google Developers Console. 
Follow this guide https://developers.google.com/sheets/api/quickstart/python to get the credentials and copy the them to
 app/utils/credentials as sakabot-cred.json. Copy the client email value in the credentials file you got and share 
the spreadsheet with that email. See app.utils/README.md for documentation on the module.

### Deployment
To deploy to Heroku, you can push to heroku with the following commands.
Be sure to be careful to have the deploy branch have ONLY one remote that points to heroku.

```
$ git checkout deploy
$ git push heroku deploy:master
```
