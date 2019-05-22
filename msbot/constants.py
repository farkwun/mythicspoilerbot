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
DUPLICATES = 'duplicates'

# Commands
HELLO_CMD = 'hello'
GOODBYE_CMD = 'goodbye'
SEND_CMD = 'unseen'
RECENT_CMD = 'recent'
MODE_CMD = 'mode'
POLL_MODE_CMD = 'poll'
ASAP_MODE_CMD = 'asap'
INFO_CMD = 'help'

# Responses
RESP_SUBBED = "You are now subscribed. Tap the '" + INFO_CMD.capitalize() + "' button (or type the command) to get some information about me and a list of my commands, or just wait for spoilers to roll in :)"
RESP_UNSUBBED = 'You have been unsubscribed from MythicSpoilerBot'
RESP_ALREADY_SUBBED = 'You are already subscribed'
RESP_ALREADY_UNSUBBED = 'You are not subscribed'
RESP_INVALID_UNSUBBED = "You are not subscribed. Tap the '" + HELLO_CMD.capitalize() + "' button (or type the command) at any time to subscribe"
RESP_INVALID_SUBBED = "Invalid command. Tap the '" + INFO_CMD.capitalize() + "' button (or type the command) to get a list of my supported commands"
RESP_UPDATE = (
    "New spoilers are out! You have {num_spoilers} unseen spoiler(s).\n\n"
    "Tap the '" + SEND_CMD.capitalize() + "' or '" + RECENT_CMD.capitalize() +
    "' buttons below.\n\n" + SEND_CMD.capitalize() + " - Receive all your unseen spoilers\n\n"
    + RECENT_CMD.capitalize() + " - Receive the most recent day of spoilers"
)
RESP_LAST_SPOILER_INFO = "These spoilers were released on {date_string} "
RESP_UPDATE_UPDATED = "No new spoilers :(. Tap the '" + RECENT_CMD.capitalize() + "' button (or type the command) to get the most recent day of spoilers"
RESP_UPDATE_COMPLETE = 'You are now up to date'
RESP_MODE_PROMPT = (
    "Change your update mode! Your current update mode is '{update_mode}'.\n\n"
    "Tap the '" + POLL_MODE_CMD.capitalize() + "' or '" + ASAP_MODE_CMD.capitalize() +
    "' buttons below.\n\n" + POLL_MODE_CMD.capitalize() + " - When new spoilers are "
    "available, I'll send a prompt so you can get spoilers at your pace\n\n"
    + ASAP_MODE_CMD.capitalize() + " - When new spoilers are available, I'll send you "
    "the spoilers as soon as I get them so you can get spoilers ASAP"
)
RESP_MODE_COMPLETE = "Your update mode is now '{update_mode}'"
RESP_INFO_PROMPT = (
    'Hi! Welcome to MSBot :D. Tap a button below (or type the command) to get started.\n\n'
    "I support the following commands:\n\n"
    + SEND_CMD.capitalize() + " - Receive all outstanding spoilers (you might not have any if you've just subscribed)\n\n"
    + RECENT_CMD.capitalize() + " - Receive the most recent day of spoilers\n\n"
    + MODE_CMD.capitalize() + " - Change your update mode! The default mode prompts you when new spoilers are available so you can get them at your own pace\n\n"
    + GOODBYE_CMD.capitalize() + " - Unsubscribe from MSBot"
)
