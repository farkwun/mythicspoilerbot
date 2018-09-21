from bottle import route, run, request, response, default_app
import json
import msbot.mslib
import requests
import time
import msbot.settings
import sqlite3
from threading import Thread

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
FB_API_URL = 'https://graph.facebook.com/v2.6/me/message_attachments?access_token=' + msbot.settings.PAGE_ACCESS_TOKEN

MODE = 'hub.mode'
TOKEN = 'hub.verify_token'
CHALLENGE = 'hub.challenge'
SUBSCRIBE = 'subscribe'

conn = sqlite3.connect('db/msbot_tables.db')
c = conn.cursor()

# Helpers
def send_message(sender_psid, response):
	request_body = {
			RECIPIENT: {
				ID: sender_psid
				},
			MESSAGE: response,
			}
	print('sending image')
	fb_url = "https://graph.facebook.com/v2.11/me/messages"
	print(str(request_body))
	params = {
			ACCESS_TOKEN: msbot.settings.PAGE_ACCESS_TOKEN,
			RECIPIENT: sender_psid
			}

	r = requests.post(fb_url, params=params, json=request_body)

#send updates from MythicSpoiler every 10 minutes
def send_updates():
	t_conn = sqlite3.connect('db/msbot_tables.db')
	tc = t_conn.cursor()
	print('thread')
	while (True):
		time.sleep(600)
		spoilers = msbot.mslib.getLatestSpoilers()
		print('spoiler get')
		tc.execute('''
			SELECT id FROM users
			''')
		current_users = tc.fetchall()
                for user in current_users:
                    for spoiler in spoilers:
                            tc.execute('''
                                    SELECT img FROM spoilers WHERE img = ?
                                    ''', (spoiler,))
                            if len(tc.fetchall()) == 0:
                                    print(spoiler)
                                    spoiler_json = {
                                            "message": {
                                                    "attachment": {
                                                            "type": "image",
                                                            "payload": {
                                                                    "is_reusable": True,
                                                                    "url": spoiler
                                                            }
                                                    }
                                            }
                                    }
                                    try:
                                            attach_response = requests.post(FB_API_URL, json = spoiler_json)
                                    except ConnectionError:
                                            print('FB Connection Error')
                                    else:
                                            attach_json = json.loads(attach_response.text)
                                            if 'attachment_id' in attach_json:
                                                    attach_id = attach_json["attachment_id"]
                                                    response = {
                                                                    "attachment": {
                                                                            "type": "image",
                                                                            "payload": {
                                                                                    "attachment_id": attach_id
                                                                            }
                                                                    }
                                                    }
                                                    send_message(user[0], response)
                                            tc.execute('''
                                                    INSERT INTO spoilers VALUES(0, ?)
                                                    ''', (spoiler,))
                                            t_conn.commit()
	
#Handle messages received from user
def handle_message(sender_psid, received_message):
	conn = sqlite3.connect('db/msbot_tables.db')
	c = conn.cursor()
	if received_message:
		print('handling message')
		print('message:', received_message)
		if received_message.lower() == 'poop':
			response = {TEXT: 'ur a poop'}
			send_message(sender_psid, response)
		elif received_message.lower() == 'hello':
			c.execute('''
				SELECT id FROM users WHERE id = ?
				''', (sender_psid,))
			if len(c.fetchall()) == 0:
				c.execute('''
					INSERT INTO users VALUES(?, 0)
					''', (sender_psid,))
				conn.commit()	
				response = {TEXT: 'You are now subscribed. Say "goodbye" at any time to unsubscribe'}
				send_message(sender_psid, response)
			else:
				response = {TEXT: 'You are already subscribed'}
				send_message(sender_psid, response)
		elif received_message.lower() == 'goodbye':
			print(sender_psid)
			c.execute('''
				DELETE FROM users WHERE id = ?
				''', (sender_psid,))
			conn.commit()
			response = {TEXT: 'You have been unsubscribed from MythicSpoilerBot'}
			send_message(sender_psid, response)
		else:
			c.execute('''
				SELECT id FROM users WHERE id = ?
				''', (sender_psid,))
			if len(c.fetchall()) == 0:
				response = {TEXT: 'Invalid command. Say "hello" at any time to subscribe'}
				send_message(sender_psid, response)
			else:
				response = {TEXT: 'Invalid command. Say "goodbye" at any time to unsubscribe'}
				send_message(sender_psid, response)

def handle_postback(sender_psid, received_postback):
	pass

@route('/webhook', method='POST')
def webhook_event():
	print('event received')
	req = json.load(request.body)

	if req[OBJECT] == PAGE_OBJECT:
		for entry in req[ENTRY]:
			event = entry[MESSAGING][0]
			sender_psid = event[SENDER][ID]

			if event[MESSAGE]:
				try:
					handle_message(sender_psid, event[MESSAGE][TEXT])
				except KeyError:
					print('Non-text message received')
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

update_thread = Thread(target = send_updates)
update_thread.setDaemon(True)
update_thread.start()
