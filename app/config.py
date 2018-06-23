import os
HOME_DIR = os.path.dirname(os.path.abspath(__file__))
# slack bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
ASSET_SPREADSHEET_KEY = os.getenv('ASSET_SPREADSHEET_KEY')
SLACK_VERIFICATION_TOKEN = os.getenv("SLACK_VERIFICATION_TOKEN")
ADMIN_SLACK_ID = os.getenv("ADMIN_SLACK_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL")
