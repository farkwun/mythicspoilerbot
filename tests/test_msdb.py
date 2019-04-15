import unittest

from msbot.msdb import MSDatabase
from msbot.settings import TEST_DB_LOCATION


class TestWebhook(unittest.TestCase):
    def setUp(self):
        def cleanup_test_db():
            self.test_db.write(
                'DROP TABLE IF EXISTS spoilers'
            )
            self.test_db.write(
                'DROP TABLE IF EXISTS users'
            )

        def setup_test_db():
            self.test_db.write(
                '''
                CREATE TABLE IF NOT EXISTS spoilers
                (date varchar(250) NOT NULL, img varchar(250) NOT NULL)
                '''
            )
            self.test_db.write(
                '''
                CREATE TABLE IF NOT EXISTS users
                (id varchar(250) NOT NULL, last varchar(250) NOT NULL)
                '''
            )

        self.test_db = MSDatabase(TEST_DB_LOCATION)
        setup_test_db()
        self.addCleanup(cleanup_test_db)

    def test_get_all_user_ids(self):
        mock_user_ids = {
            'Alice',
            'Bob',
            'Carol',
        }

        for mock_id in mock_user_ids:
            self.test_db.write(
                'INSERT INTO users VALUES(?, 0)',
                (mock_id,)
            )

        self.assertEqual(
            mock_user_ids,
            { e for e in self.test_db.get_all_user_ids() }
        )

    def test_spoiler_exists(self):
        test_spoiler = 'test_spoiler_img'
        self.assertFalse(self.test_db.spoiler_exists(test_spoiler))
        self.test_db.write(
            'INSERT INTO spoilers VALUES(0, ?)',
            (test_spoiler,)
        )
        self.assertTrue(self.test_db.spoiler_exists(test_spoiler))

    def test_user_exists(self):
        test_user = 'test_user_id'
        self.assertFalse(self.test_db.user_exists(test_user))
        self.test_db.write(
            'INSERT INTO users VALUES(?, 0)',
            (test_user,)
        )
        self.assertTrue(self.test_db.user_exists(test_user))

    def test_add_user(self):
        test_user = 'test_user_id'
        self.test_db.query(
            'SELECT id FROM users where id = ?',
            (test_user,)
        )
        self.assertFalse(self.test_db.fetchall())

        self.test_db.add_user(test_user)

        self.test_db.query(
            'SELECT id FROM users where id = ?',
            (test_user,)
        )
        self.assertTrue(self.test_db.fetchall())

    def test_delete_user(self):
        test_user = 'test_user_id'
        self.test_db.write(
            'INSERT INTO users VALUES(?, 0)',
            (test_user,)
        )
        self.test_db.query(
            'SELECT id FROM users where id = ?',
            (test_user,)
        )
        self.assertTrue(self.test_db.fetchall())

        self.test_db.delete_user(test_user)

        self.test_db.query(
            'SELECT id FROM users where id = ?',
            (test_user,)
        )
        self.assertFalse(self.test_db.fetchall())

    def test_add_spoiler(self):
        test_spoiler = 'test_spoiler_img'
        self.test_db.query(
            'SELECT img FROM spoilers where img = ?',
            (test_spoiler,)
        )
        self.assertFalse(self.test_db.fetchall())

        self.test_db.add_spoiler(test_spoiler)

        self.test_db.query(
            'SELECT img FROM spoilers where img = ?',
            (test_spoiler,)
        )
        self.assertTrue(self.test_db.fetchall())

    def test_create_spoilers(self):
        self.test_db.write(
            'DROP TABLE IF EXISTS spoilers'
        )

        self.test_db.create_spoilers()

        self.test_db.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='spoilers'"
        )
        self.assertTrue(self.test_db.fetchall())

    def test_create_users(self):
        self.test_db.write(
            'DROP TABLE IF EXISTS users'
        )

        self.test_db.create_users()

        self.test_db.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        self.assertTrue(self.test_db.fetchall())
