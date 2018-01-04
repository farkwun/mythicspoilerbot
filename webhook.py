from bottle import route, run, request, response, default_app
import json
import msbot.mslib
import requests

import msbot.settings

# Constants
OBJECT = 'object'
PAGE_OBJECT = 'page'
ENTRY = 'entry'
MESSAGING = 'messaging'
MESSAGE = 'message'
SENDER = 'sender'
ID = 'id'
POSTBACK = 'postback'
TEXT = 'text'
RECIPIENT = 'recipient'
ACCESS_TOKEN = 'access_token'

MODE = 'hub.mode'
TOKEN = 'hub.verify_token'
CHALLENGE = 'hub.challenge'
SUBSCRIBE = 'subscribe'

# Helpers
def call_send_API(sender_psid, response):
    request_body = {
        RECIPIENT: {
            ID: sender_psid
        },
        MESSAGE: response,
    }

    fb_url = "https://graph.facebook.com/v2.11/me/messages"

    params = {
        ACCESS_TOKEN: msbot.settings.PAGE_ACCESS_TOKEN,
        RECIPIENT: sender_psid
    }

    r = requests.post(fb_url, params=params, json=request_body)

def handle_message(sender_psid, received_message):
    if received_message[TEXT]:
        response = {
            TEXT: "You sent the message '%s'. Now send me an image!" %
            received_message[TEXT]
        }
    call_send_API(sender_psid, response)

def handle_postback(sender_psid, received_postback):
    pass


@route('/webhook', method='POST')
def webhook_event():
    req = json.load(request.body)

    if req[OBJECT] == PAGE_OBJECT:
        for entry in req[ENTRY]:
            event = entry[MESSAGING][0]
            sender_psid = event[SENDER][ID]

            if event[MESSAGE]:
                handle_message(sender_psid, event[MESSAGE])
            elif event[POSTBACK]:
                handle_postback(sender_psid, event[POSTBACK])
        response.status = 200
        return 'EVENT_RECEIVED'
    else:
        response.status = 404


@route('/webhook', method='GET')
def webhook_verify():
    mode = request.query[MODE]
    token = request.query[TOKEN]
    challenge = request.query[CHALLENGE]

    if mode and token:
        if mode == SUBSCRIBE and token == msbot.settings.VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            response.status = 200
            return challenge
        else:
            response.status = 403

if __name__ == '__main__':
    run(host='0.0.0.0', port=8080)
else:
    app = application = default_app()
