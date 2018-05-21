import os
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
# slack bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
# get from env or use default mongo uri
MONGODB_URI = os.getenv('MONGODB_URI')
ASSET_SPREADSHEET_KEY = os.getenv('ASSET_SPREADSHEET_KEY')
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
