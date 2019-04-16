from msbot.db import Database
from msbot.spoiler import Spoiler
from msbot.user import User


class MSDatabase(Database):
    def get_user_from_id(self, user_id):
        sql = "SELECT * FROM users WHERE id = '{user_id}'".format(user_id=user_id)
        self.query(sql)
        return User(self.fetchone())

    def get_spoiler_from_id(self, spoiler_id):
        sql = "SELECT * FROM spoilers WHERE id = '{spoiler_id}'".format(spoiler_id=spoiler_id)
        self.query(sql)
        return Spoiler(self.fetchone())

    def get_all_user_ids(self):
        sql = 'SELECT id FROM users'
        self.query(sql)
        return [ user_id for (user_id,) in self.fetchall() ]

    def get_all_users(self):
        sql = 'SELECT * FROM users'
        self.query(sql)
        return [ User(row) for row in self.fetchall() ]

    def get_all_unnotified_users(self):
        sql = "SELECT * FROM users WHERE last < {last_spoiled}".format(last_spoiled=self.get_latest_spoiler_id())
        self.query(sql)
        return [ User(row) for row in self.fetchall() ]

    def update_user(self, user_id, last=None):
        if last != None:
            sql = "UPDATE users SET last = {last} WHERE id = '{user}'".format(last=last, user=user_id)
            self.write(sql)

    def spoiler_exists(self, spoiler):
        sql = "SELECT img FROM spoilers WHERE img = '{spoiler}'".format(spoiler=spoiler)
        self.query(sql)
        return len(self.fetchall()) != 0

    def user_exists(self, user_id):
        sql = "SELECT id FROM users where id = '{user_id}'".format(user_id=user_id)
        self.query(sql)
        return len(self.fetchall()) != 0

    def add_user(self, user_id):
        sql = "INSERT INTO users VALUES('{user_id}', '{last_spoiler}')".format(
            user_id=user_id,
            last_spoiler=self.get_latest_spoiler_id()
        )
        self.write(sql)

    def delete_user(self, user_id):
        sql = "DELETE FROM users where id = '{user_id}'".format(user_id=user_id)
        self.write(sql)

    def add_spoiler(self, spoiler_img, attach_id):
        sql = '''
        INSERT INTO spoilers VALUES('{spoiler_img}', '{attach_id}', NULL)
        '''.format(
            spoiler_img=spoiler_img,
            attach_id=attach_id
        )
        self.write(sql)

    def get_latest_spoiler_id(self):
        sql = "SELECT MAX(id) FROM spoilers"
        self.query(sql)
        (latest_id,) = self.fetchone()
        return latest_id if latest_id != None else 0

    def get_all_spoilers(self):
        sql = 'SELECT * FROM spoilers'
        self.query(sql)
        return [ Spoiler(row) for row in self.fetchall() ]

    def get_spoilers_later_than(self, row_id):
        sql = 'SELECT * FROM spoilers WHERE id > {row_id}'.format(row_id=row_id)
        self.query(sql)
        return [ Spoiler(row) for row in self.fetchall() ]

    def create_spoilers_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS spoilers (
            img varchar(250) NOT NULL,
            attach_id VARCHAR(50) NOT NULL,
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
        '''
        self.write(sql)

    def create_users_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id varchar(250) NOT NULL,
            last INTEGER NOT NULL
        )
        '''
        self.write(sql)
