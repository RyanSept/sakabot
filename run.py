from gevent import monkey
monkey.patch_all()

from app import slack_events_adapter, huey
from app import views
import logging


if __name__ == "__main__":
    # logging.basicConfig(filename="example.log", level=logging.DEBUG)
    huey.start()
    slack_events_adapter.start(port=5000, debug=True)
