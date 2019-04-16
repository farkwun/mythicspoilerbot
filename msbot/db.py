import sqlite3


# Base class sourced from - https://stackoverflow.com/a/38078544
class Database(object):
    def __init__(self, name):
        self._conn = sqlite3.connect(name)
        self._cursor = self._conn.cursor()

    def enter(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def write(self, sql, params=None):
        self.query(sql, params)
        self.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def drop_table(self, table_name):
        self._cursor.execute(
            '''
            DROP TABLE IF EXISTS {table_name}
            '''.format(table_name=table_name)
        )
