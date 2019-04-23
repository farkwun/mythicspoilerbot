import json
from msbot.msdb import MSDatabase
from msbot.user_options import UserOptions

old_db = MSDatabase('db/test_table_copy.db')
new_db = MSDatabase('db/test_table.db')

new_db.drop_table('spoilers')
new_db.drop_table('users')

new_db.create_spoilers_table()
new_db.create_users_table()

sql = "SELECT img, attach_id FROM spoilers"
old_db.query(sql)
old_spoilers = old_db.fetchall()

sql = "SELECT id, last_updated, last_spoiled FROM users"
old_db.query(sql)
old_users = old_db.fetchall()

for img, attach_id in old_spoilers:
    sql = "INSERT INTO spoilers VALUES('{}', '{}', '2019-04-17', NULL)".format(img, attach_id)
    new_db.write(sql)

options = UserOptions.default_options()
for id, last_updated, last_spoiled in old_users:
    sql = "INSERT INTO users VALUES ('{}', {}, {}, '{}')".format(
        id,
        last_updated,
        last_spoiled,
        json.dumps(options)
    )
    new_db.write(sql)
