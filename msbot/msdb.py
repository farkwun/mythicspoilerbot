import json
import msbot.constants

from msbot.db import Database
from msbot.spoiler import Spoiler
from msbot.user import User
from msbot.user_options import UserOptions


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
        sql = "SELECT * FROM users WHERE last_updated < {last_spoiled}".format(last_spoiled=self.get_latest_spoiler_id())
        self.query(sql)
        return [ User(row) for row in self.fetchall() ]

    def update_user(self,
                    user_id,
                    last_updated=None,
                    last_spoiled=None,
                    options=None
    ):
        if last_updated == None and last_spoiled == None and options == None:
            return

        update_strings = []

        if last_updated != None:
            update_strings.append('last_updated = {}'.format(last_updated))

        if last_spoiled != None:
            update_strings.append('last_spoiled = {}'.format(last_spoiled))

        if options != None:
            sql = "SELECT options FROM users where id = '{}'".format(user_id)
            self.query(sql)
            (json_string,) = self.fetchone()
            user_options = json.loads(json_string)
            for key, value in options.items():
                user_options[key] = value
            update_strings.append(
                "options = '{}'".format(json.dumps(user_options))
            )

        update_string = ','.join(update_strings)

        sql = "UPDATE users SET {update_string} WHERE id = '{user_id}'".format(
            update_string=update_string,
            user_id=user_id
        )
        self.write(sql)

    def spoiler_exists(self, spoiler_img):
        sql = "SELECT img FROM spoilers WHERE img = '{spoiler}'".format(spoiler=spoiler_img)
        self.query(sql)
        return len(self.fetchall()) != 0

    def user_exists(self, user_id):
        sql = "SELECT id FROM users where id = '{user_id}'".format(user_id=user_id)
        self.query(sql)
        return len(self.fetchall()) != 0

    def add_user(self, user_id):
        latest_spoiler = self.get_latest_spoiler_id()
        sql = "INSERT INTO users VALUES('{user_id}', '{last_updated}', '{last_spoiled}', '{options_json}')".format(
            user_id=user_id,
            last_updated=latest_spoiler,
            last_spoiled=latest_spoiler,
            options_json=json.dumps(
                UserOptions.default_options()
            )
        )
        self.write(sql)

    def delete_user(self, user_id):
        sql = "DELETE FROM users where id = '{user_id}'".format(user_id=user_id)
        self.write(sql)

    def add_spoiler(self, spoiler_img, attach_id):
        sql = '''
        INSERT INTO spoilers VALUES('{spoiler_img}', '{attach_id}',
        DATE('now'), NULL)
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

    def get_latest_spoiler_date(self):
        sql = 'SELECT MAX(date_spoiled) FROM spoilers'
        self.query(sql)
        (date,) = self.fetchone()
        return date

    def get_all_spoilers_on_date(self, date):
        sql = "SELECT * FROM spoilers WHERE date_spoiled = '{date}'".format(date=date)
        self.query(sql)
        return [ Spoiler(row) for row in self.fetchall() ]

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
            date_spoiled TEXT NOT NULL,
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
        '''
        self.write(sql)

    def create_users_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id varchar(250) NOT NULL,
            last_updated INTEGER NOT NULL,
            last_spoiled INTEGER NOT NULL,
            options JSON NOT NULL,
            FOREIGN KEY (last_updated) REFERENCES spoiler(id),
            FOREIGN KEY (last_spoiled) REFERENCES spoiler(id)
        )
        '''
        self.write(sql)
