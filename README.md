# Sakabot
Sakabot is a slackbot designed to help Andelans find the owners of lost and found equipment. It is built off of Slack's Events API.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites
Python 3.6.x

[Python Slack Events API](https://github.com/slackapi/python-slack-events-api)

## Installing
1. Clone the repo from Github by running  `$ git clone git@github.com:RyanSept/sakabot.git`

2. Change directory into package `$ cd sakabot`

3. Install the dependencies by running `$ pip install requirements.txt`

4. Create a .env file from the .env.sample file, populating it with values you'll find on the Slack app page. You can then dump the variables into your environment by running `$ source .env`


Before running the app, you need to setup the datastore and populate it by running the extractor on the asset/work tools spreadsheet. To run the extractor, you need Google API credentials. To get these, you need to setup a project on the Google Developers Console.
Follow this guide https://developers.google.com/sheets/api/quickstart/python to get the credentials and download the _Client Configuration_ file to
 app/utils/credentials as the file _sakabot-cred.json_. Copy the client email value in the credentials file you got and share
the spreadsheet with that email. See [this other readme](app/utils/README.md) for documentation on the module.

## Creating the Slack App
1. Go to https://api.slack.com/apps and click on `Create new app`.

2. Once you've given it a name and chosen, the workspace, you will be redirected to the app's page.

3. Navigate to `Add features and functionality > Bots` and click on add a bot user. Give it a name and check the `Always Show My Bot as Online
` checkbox and then click "Create bot user".

4. On the app page, go to `Add features and functionality > Event Subscriptions`. Enable events and insert the webhook uri for events eg. `https://sakabot.herokuapp.com/slack/events`

5. Still on the events page, on the `Subscribe to Bot Events` section, add the bot user events *app_mention* and *message.im*. Save changes and go back to the app page.

6. On the app page and navigate to `Add features and functionality > Interactivity`. Switch on Interactivity. Insert the api endpoint uri eg. `https://sakabot.herokuapp.com/interactive`

You're done!

## Deployment
```
$ git checkout deploy
$ git push heroku deploy:master
```
