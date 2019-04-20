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

def send_text_message(sender_psid, text):
    send_message(sender_psid, { msbot.constants.TEXT: text})

def create_quick_reply_button(payload):
    return {
        msbot.constants.CONTENT_TYPE: msbot.constants.TEXT,
        msbot.constants.TITLE: payload.capitalize(),
        msbot.constants.PAYLOAD: payload,
    }

def send_update(sender_psid, text):
    resp = {
        msbot.constants.TEXT: text,
        msbot.constants.QUICK_REPLIES: [
            create_quick_reply_button(msbot.constants.SEND),
            create_quick_reply_button(msbot.constants.RECENT),
        ]
    }
    send_message(sender_psid, resp)

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

def update_user(user):
    db = msbot.msdb.MSDatabase(db_file)
    last_spoiler = db.get_latest_spoiler_id()

    def poll(user):
        num_spoilers = last_spoiler - user.last_spoiled
        resp = msbot.constants.RESP_UPDATE.format(num_spoilers=num_spoilers)
        send_update(user.user_id, resp)

    def asap(user):
        handle_message(user.user_id, msbot.constants.SEND)

    update_modes = {
        msbot.constants.POLL_MODE: lambda user: poll(user),
        msbot.constants.ASAP_MODE: lambda user: asap(user),
    }

    user_mode = user.options.update_mode

    if user_mode in update_modes:
        update_modes[user_mode](user)
    else:
        poll(user)

    db.update_user(user.user_id, last_updated=last_spoiler)

def update_users():
    db = msbot.msdb.MSDatabase(db_file)
    unnotified_users = db.get_all_unnotified_users()
    for user in unnotified_users:
        update_user(user)

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

    def send(sender_psid):
        if database.user_exists(sender_psid):
            user = database.get_user_from_id(sender_psid)
            last_spoiler = database.get_latest_spoiler_id()
            spoilers = database.get_spoilers_later_than(user.last_spoiled)
            if not spoilers:
                return msbot.constants.RESP_UPDATE_UPDATED
            for spoiler in spoilers:
                send_spoiler_to(user, spoiler)
            database.update_user(user.user_id, last_spoiled=last_spoiler)
            return msbot.constants.RESP_UPDATE_COMPLETE
        return msbot.constants.RESP_INVALID_UNSUBBED

    def recent(sender_psid):
        if database.user_exists(sender_psid):
            user = database.get_user_from_id(sender_psid)
            last_spoiler = database.get_latest_spoiler_id()
            last_spoil_date = database.get_latest_spoiler_date()
            spoilers = database.get_all_spoilers_on_date(last_spoil_date)
            for spoiler in spoilers:
                send_spoiler_to(user, spoiler)
            database.update_user(
                user.user_id,
                last_updated=last_spoiler,
                last_spoiled=last_spoiler
            )
            return msbot.constants.RESP_LAST_SPOILER_INFO.format(date_string=last_spoil_date)
        return msbot.constants.RESP_INVALID_UNSUBBED

    responses = {
        msbot.constants.HELLO: lambda id: subscribe(id),
        msbot.constants.GOODBYE: lambda id: unsubscribe(id),
        msbot.constants.SEND: lambda id: send(id),
        msbot.constants.RECENT: lambda id: recent(id),
    }
    message = received_message.lower()
    if message in responses:
        resp = responses[message](sender_psid)
    else:
        resp = msbot.constants.RESP_INVALID_UNSUBBED
        if database.user_exists(sender_psid):
            resp = msbot.constants.RESP_INVALID_SUBBED

    send_text_message(sender_psid, resp)

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
