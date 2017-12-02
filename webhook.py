from bottle import route, run, request, response
import json

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


run(host='localhost', port=8080)
