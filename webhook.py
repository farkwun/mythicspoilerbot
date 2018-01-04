from bottle import route, run, request, response, default_app
import json
import msbot.mslib
import requests
import time
import msbot.settings
import sqlite3


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

conn = sqlite3.connect('db/msbot_tables.db')
c = conn.cursor()

# Helpers
def send_image(sender_psid, response):
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
	images = msbot.mslib.getSpoilersTest(0)
	response = {TEXT: '0'}
	send_image(sender_psid, response)
	for image in images:
	        c.execute('''
	                SELECT img FROM spoilers WHERE img = ?
	                ''', (image,))
	        if len(c.fetchall()) == 0:
	                response = {TEXT: image}
			send_image(sender_psid, response)
	                c.execute('''
	                        INSERT INTO spoilers VALUES(0, ?)
	                        ''', (image,))
	images = msbot.mslib.getSpoilersTest(1)
	response = {TEXT: '1'}
        send_image(sender_psid, response)
	for image in images:
	        c.execute('''
	                SELECT img FROM spoilers WHERE img = ?
	                ''', (image,))
	        if len(c.fetchall()) == 0:
	                response = {TEXT: image}
                        send_image(sender_psid, response)
			c.execute('''
	                        INSERT INTO spoilers VALUES(0, ?)
	                        ''', (image,))

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
