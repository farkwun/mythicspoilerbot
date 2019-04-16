from msbot.msdb import MSDatabase

new_db = MSDatabase('db/msbot_tables.db')

new_db.drop_table('spoilers')
new_db.drop_table('users')

new_db.create_spoilers_table()
new_db.create_users_table()
