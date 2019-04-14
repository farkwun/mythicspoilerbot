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

def get_attach_dict_for(images):
    return { image_url: get_attach_id_for(image_url) for image_url in images }

def send_spoiler_to(user_id, attach_id):
    response = {
        "attachment": {
            "type": "image",
            "payload": {
                "attachment_id": attach_id
            }
        }
    }
    send_message(user_id, response)

#send updates from MythicSpoiler every 10 minutes
def send_updates():
    database = msbot.msdb.MSDatabase(db_file)
    while True:
        time.sleep(600)
        spoilers = [
            s for s in msbot.mslib.getLatestSpoilers() if not
            database.spoiler_exists(s)
        ]
        attach_dict = get_attach_dict_for(spoilers)
        current_users = database.get_all_user_ids()

        for (user_id,) in current_users:
            for spoiler in spoilers:
                send_spoiler_to(user_id, attach_dict[spoiler])

        for spoiler, attach_id in attach_dict.items():
            database.add_spoiler(spoiler)

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

    send_message(sender_psid, {msbot.constants.TEXT: resp})

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

            if event[msbot.constants.MESSAGE]:
                try:
                    if sender_psid == u'1611805388885188':
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

update_thread = Thread(target = send_updates)
update_thread.setDaemon(True)
update_thread.start()
