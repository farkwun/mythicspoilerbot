from msbot.db import Database


class MSDatabase(Database):
    def get_all_user_ids(self):
        sql = 'SELECT id FROM users'
        self.query(sql)
        return [ user_id for (user_id,) in self.fetchall() ]

    def spoiler_exists(self, spoiler):
        sql = 'SELECT img FROM spoilers WHERE img = ?'
        self.query(sql, (spoiler,))
        return len(self.fetchall()) != 0

    def user_exists(self, user_id):
        sql = 'SELECT id FROM users where id = ?'
        self.query(sql, (user_id,))
        return len(self.fetchall()) != 0

    def add_user(self, user_id):
        sql = 'INSERT INTO users VALUES(?, 0)'
        self.write(sql, (user_id,))

    def delete_user(self, user_id):
        sql = 'DELETE FROM users where id = ?'
        self.write(sql, (user_id,))

    def add_spoiler(self, spoiler_img):
        sql = 'INSERT INTO spoilers VALUES(0, ?)'
        self.write(sql, (spoiler_img,))

    def create_spoilers(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS spoilers
        (date varchar(250) NOT NULL, img varchar(250) NOT NULL)
        '''
        self.write(sql)

    def create_users(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users
        (id varchar(250) NOT NULL, last varchar(250) NOT NULL)
        '''
        self.write(sql)
