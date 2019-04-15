import webhook
import msbot.msdb
import msbot.constants

db_file = 'db/broadcast_table.db'

database = msbot.msdb.MSDatabase(db_file)

broadcast_users = database.get_all_user_ids()

message = 'Hello World!'

for user_id in broadcast_users:
    webhook.send_message(user, { msbot.constants.TEXT: message })
