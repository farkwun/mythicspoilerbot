from msbot.db import Database


class MSDatabase(Database):
    def get_all_user_ids(self):
        sql = 'SELECT id FROM users'
        self.query(sql)
        return [ user_id for (user_id,) in self.fetchall() ]

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
        self.write(sql)
        (latest_id,) = self.fetchone()
        return latest_id

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
            last varchar(250) NOT NULL
        )
        '''
        self.write(sql)
