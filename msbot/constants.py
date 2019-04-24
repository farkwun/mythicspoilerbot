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
UPDATE_MODE = 'update_mode'

# Commands
HELLO_CMD = 'hello'
GOODBYE_CMD = 'goodbye'
SEND_CMD = 'all'
RECENT_CMD = 'recent'
MODE_CMD = 'mode'
POLL_MODE_CMD = 'poll'
ASAP_MODE_CMD = 'asap'

# Responses
RESP_SUBBED = "You are now subscribed. Say 'goodbye' at any time to unsubscribe"
RESP_UNSUBBED = 'You have been unsubscribed from MythicSpoilerBot'
RESP_ALREADY_SUBBED = 'You are already subscribed'
RESP_ALREADY_UNSUBBED = 'You are not subscribed'
RESP_INVALID_UNSUBBED = "Invalid command. Say 'hello' at any time to subscribe"
RESP_INVALID_SUBBED = "Invalid command. Say 'recent' to get the latest batch of spoilers or say 'goodbye' at any time to unsubscribe"
RESP_UPDATE = (
    "New spoilers are out! You have {num_spoilers} unseen spoiler(s).\n\n"
    "Choose the '" + SEND_CMD.capitalize() + "' or '" + RECENT_CMD.capitalize() +
    "' buttons below.\n\n" + SEND_CMD.capitalize() + " - Receive all unseen spoilers\n\n"
    + RECENT_CMD.capitalize() + " - Receive most recent spoilers and mark remaining as seen"
)
RESP_LAST_SPOILER_INFO = "These spoilers were released on {date_string} "
RESP_UPDATE_UPDATED = 'No new spoilers :('
RESP_UPDATE_COMPLETE = 'You are now up to date'
RESP_MODE_PROMPT = (
    "Change your update mode! Your current update mode is '{update_mode}'.\n\n"
    "Choose the '" + POLL_MODE_CMD.capitalize() + "' or '" + ASAP_MODE_CMD.capitalize() +
    "' buttons below.\n\n" + POLL_MODE_CMD.capitalize() + " - When new spoilers are "
    "available, I'll send a prompt so you can get spoilers at your pace\n\n"
    + ASAP_MODE_CMD.capitalize() + " - When new spoilers are available, I'll send you "
    "the spoilers as soon as I get them so you can get spoilers ASAP"
)
RESP_MODE_COMPLETE = "Your update mode is now '{update_mode}'"
