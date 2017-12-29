from bottle import route, run, request, response, default_app
import json
import msbot.mslib
import msbot.settings

# Constants
OBJECT = 'object'
PAGE_OBJECT = 'page'
ENTRY = 'entry'
MESSAGING = 'messaging'
MESSAGE = 'message'

MODE = 'hub.mode'
TOKEN = 'hub.verify_token'
CHALLENGE = 'hub.challenge'
SUBSCRIBE = 'subscribe'

# Helpers
def handle_message(sender_psid, received_message):
    pass

def handle_postback(sender_psid, received_postback):
    pass

def call_send_API(sender_psid, response):
    pass

@route('/webhook', method='POST')
def webhook_event():
    req = json.load(request.body)

    if req[OBJECT] == PAGE_OBJECT:
        for entry in req[ENTRY]:
            print(entry[MESSAGING][0][MESSAGE])
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
