import msbot.settings

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
FB_MESSAGE_URL = 'https://graph.facebook.com/v2.11/me/messages'

MODE = 'hub.mode'
TOKEN = 'hub.verify_token'
CHALLENGE = 'hub.challenge'
SUBSCRIBE = 'subscribe'

QUICK_REPLIES = 'quick_replies'
CONTENT_TYPE = 'content_type'
TITLE = 'title'
PAYLOAD = 'payload'

# Commands
HELLO = 'hello'
GOODBYE = 'goodbye'
SEND = 'all'
RECENT = 'recent'
UPDATE_MODE = 'update_mode'
POLL_MODE = 'poll'
ASAP_MODE = 'asap'

# Responses
RESP_SUBBED = "You are now subscribed. Say 'goodbye' at any time to unsubscribe"
RESP_UNSUBBED = 'You have been unsubscribed from MythicSpoilerBot'
RESP_ALREADY_SUBBED = 'You are already subscribed'
RESP_ALREADY_UNSUBBED = 'You are not subscribed'
RESP_INVALID_UNSUBBED = "Invalid command. Say 'hello' at any time to subscribe"
RESP_INVALID_SUBBED = "Invalid command. Say 'recent' to get the latest batch of spoilers or say 'goodbye' at any time to unsubscribe"
RESP_UPDATE = (
    "New spoilers are out! You have {num_spoilers} unseen spoiler(s).\n\n"
    "Choose the '" + SEND.capitalize() + "' or '" + RECENT.capitalize() +
    "' buttons below.\n\n" + SEND.capitalize() + " - Receive all unseen spoilers\n\n"
    + RECENT.capitalize() + " - Receive most recent spoilers and mark remaining as seen"
)
RESP_LAST_SPOILER_INFO = "These spoilers were released on {date_string} "
RESP_UPDATE_UPDATED = 'No new spoilers :('
RESP_UPDATE_COMPLETE = 'You are now up to date'
