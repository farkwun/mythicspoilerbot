from bottle import route, run, request, response, default_app
import json
import msbot.constants
import msbot.mslib
import msbot.msdb
import requests
import time
import msbot.settings
import sqlite3
from threading import Thread

db_file = msbot.settings.DB_LOCATION

# Helpers
def send_message(sender_psid, response):
    request_body = {
        msbot.constants.RECIPIENT: {
            msbot.constants.ID: sender_psid
        },
        msbot.constants.MESSAGE: response,
    }
    print('sending image')
    print(str(request_body))
    params = {
        msbot.constants.ACCESS_TOKEN: msbot.settings.PAGE_ACCESS_TOKEN,
        msbot.constants.RECIPIENT: sender_psid
    }

    r = requests.post(msbot.constants.FB_MESSAGE_URL, params=params, json=request_body)


def get_attach_id_for(image_url):
    print('Getting attach id for ', image_url)
    body = {
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "is_reusable": True,
                    "url": image_url
                }
            }
        }
    }
    try:
        attach_response = requests.post(msbot.constants.FB_API_URL, json=body)
    except ConnectionError:
        print('FB Connection Error')
    else:
        return json.loads(attach_response.text)['attachment_id']

def send_spoiler_to(user, spoiler):
    db = msbot.msdb.MSDatabase(db_file)
    response = {
        "attachment": {
            "type": "image",
            "payload": {
                "attachment_id": spoiler.attach_id
            }
        }
    }
    send_message(user.user_id, response)

def update_spoilers():
    db = msbot.msdb.MSDatabase(db_file)
    spoilers = [
        s for s in msbot.mslib.getLatestSpoilers() if not
        db.spoiler_exists(s)
    ]
    attach_dict = { s: get_attach_id_for(s) for s in spoilers }
    for spoiler, attach_id in attach_dict.items():
        db.add_spoiler(spoiler, attach_id)

def update_users():
    db = msbot.msdb.MSDatabase(db_file)
    current_users = db.get_all_unnotified_users()
    earliest_id = last_spoiler = db.get_latest_spoiler_id()

    for user in current_users:
        if user.last_spoiled < earliest_id:
            earliest_id = user.last_spoiled

    spoilers = db.get_spoilers_later_than(earliest_id)

    for user in current_users:
        for spoiler in spoilers:
            if spoiler.spoiler_id > user.last_spoiled:
                send_spoiler_to(user, spoiler)
        db.update_user(user.user_id, last=last_spoiler)

#send updates from MythicSpoiler every 10 minutes
def update():
    while True:
        time.sleep(600)
        update_spoilers()
        update_users()

#Handle messages received from user
def handle_message(sender_psid, received_message):
    database = msbot.msdb.MSDatabase(db_file)
    def subscribe(sender_psid):
        if not database.user_exists(sender_psid):
            database.add_user(sender_psid)
            return msbot.constants.RESP_SUBBED
        return msbot.constants.RESP_ALREADY_SUBBED

    def unsubscribe(sender_psid):
        if database.user_exists(sender_psid):
            database.delete_user(sender_psid)
            return msbot.constants.RESP_UNSUBBED
        return msbot.constants.RESP_ALREADY_UNSUBBED

    responses = {
        msbot.constants.HELLO: lambda id: subscribe(id),
        msbot.constants.GOODBYE: lambda id: unsubscribe(id),
    }
    message = received_message.lower()
    if message in responses:
        resp = responses[message](sender_psid)
    else:
        resp = msbot.constants.RESP_INVALID_UNSUBBED
        if database.user_exists(sender_psid):
            resp = msbot.constants.RESP_INVALID_SUBBED

    send_message(sender_psid, { msbot.constants.TEXT: resp })

def handle_postback(sender_psid, received_postback):
    pass

@route('/webhook', method='POST')
def webhook_event():
    print('event received')
    req = json.loads(request.body.getvalue().decode('utf-8'))

    if req[msbot.constants.OBJECT] == msbot.constants.PAGE_OBJECT:
        for entry in req[msbot.constants.ENTRY]:
            event = entry[msbot.constants.MESSAGING][0]
            sender_psid = event[msbot.constants.SENDER][msbot.constants.ID]
            print("GOT MESSAGE FROM ", sender_psid)

            if event[msbot.constants.MESSAGE]:
                try:
                    if sender_psid in msbot.settings.DEV_SAFELIST:
                        handle_message(sender_psid, event[msbot.constants.MESSAGE][msbot.constants.TEXT])
                except KeyError:
                    print('Non-text message received')
            elif event[msbot.constants.POSTBACK]:
                handle_postback(sender_psid, event[msbot.constants.POSTBACK])
        response.status = 200
        return 'EVENT_RECEIVED'
    else:
        response.status = 404


@route('/webhook', method='GET')
def webhook_verify():
    mode = request.query[msbot.constants.MODE]
    token = request.query[msbot.constants.TOKEN]
    challenge = request.query[msbot.constants.CHALLENGE]

    if mode and token:
        if mode == msbot.constants.SUBSCRIBE and token == msbot.settings.VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            response.status = 200
            return challenge
        else:
            response.status = 403

if __name__ == '__main__':
    run(host='0.0.0.0', port=8080)
else:
    app = application = default_app()

update_thread = Thread(target = update)
update_thread.setDaemon(True)
update_thread.start()
