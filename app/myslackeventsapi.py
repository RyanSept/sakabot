"""
This file contains a modified version of the SlackEventAdapter and SlackServer
provided by the SlackEventsApi lib. We event handling asynchronous.
"""
from slackeventsapi import SlackEventAdapter, SlackServer
from flask import request, make_response
import json


class MySlackServer(SlackServer):
    """
    Override bind_route method to make
    """
    def bind_route(self, server):
        @server.route(self.endpoint, methods=['GET', 'POST'])
        def event():
            # If a GET request is made, return 404.
            if request.method == 'GET':
                return make_response(
                    "These are not the slackbots you're looking for.", 404)

            # Parse the request payload into JSON
            event_data = json.loads(request.data.decode('utf-8'))

            # Echo the URL verification challenge code
            if "challenge" in event_data:
                return make_response(
                    event_data.get("challenge"), 200, {"content_type":
                                                       "application/json"}
                )

            # Verify the request token
            request_token = event_data.get("token")
            if self.verification_token != request_token:
                self.emitter.emit('error', 'invalid verification token')
                return make_response(
                    "Request contains invalid Slack verification token", 403)

            # Parse the Event payload and emit the event to the event listener
            if "event" in event_data:
                event_type = event_data["event"]["type"]
                from app import huey

                @huey.task()
                def call_event_listener_async():
                    self.emitter.emit(event_type, event_data)

                # enqueue event
                call_event_listener_async()
                response = make_response("", 200)
                response.headers['X-Slack-Powered-By'] = self.package_info
                return response


class MySlackEventAdapter(SlackEventAdapter):
    """
    Rig SlackEventAdapter to use our modified SlackServer
    """
    def __init__(self, verification_token, endpoint="/slack/events",
                 server=None):
        super().__init__(verification_token, endpoint="/slack/events",
                         server=None)
        self.server = MySlackServer(verification_token, endpoint, self, server)
