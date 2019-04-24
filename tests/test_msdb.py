import unittest
import datetime
import json
import msbot.constants

from msbot.msdb import MSDatabase
from msbot.settings import TEST_DB_LOCATION
from msbot.spoiler import Spoiler
from msbot.user import User


class TestMSDatabase(unittest.TestCase):
    def setUp(self):
        def cleanup_test_db():
            self.test_db.drop_table('spoilers')
            self.test_db.drop_table('users')

        def setup_test_db():
            self.test_db.create_spoilers_table()
            self.test_db.create_users_table()

        self.test_db = MSDatabase(TEST_DB_LOCATION)
        setup_test_db()
        self.addCleanup(cleanup_test_db)

    def test_get_user_from_id(self):
        user = User(('Alice', 0, 0, '{}'))
        self.insert_user(user)
        self.assertEqual(user, self.test_db.get_user_from_id('Alice'))

    def test_get_spoiler_from_id(self):
        spoiler = Spoiler(('spoil1', 'attach1', '2019-01-01', 1234))
        self.insert_spoiler(spoiler)
        self.assertEqual(spoiler, self.test_db.get_spoiler_from_id(1234))

    def test_get_all_users(self):
        mock_users = [
            User(('Alice', 0, 0, '{}')),
            User(('Bob', 1, 1, '{}')),
            User(('Carol', 2, 2, '{}')),
        ]

        for user in mock_users:
            self.insert_user(user)

        self.assertCountEqual(
            mock_users,
            self.test_db.get_all_users()
        )

    def test_get_all_user_ids(self):
        mock_user_ids = {
            'Alice',
            'Bob',
            'Carol',
        }

        for mock_id in mock_user_ids:
            self.test_db.write(
                "INSERT INTO users VALUES('{mock_id}', 0, 0, '{{}}')".format(mock_id=mock_id)
            )

        self.assertEqual(
            mock_user_ids,
            { e for e in self.test_db.get_all_user_ids() }
        )

    def test_get_all_unnotified_users(self):
        alice = User(('Alice', 0, 2, '{}'))
        bob = User(('Bob', 1, 0, '{}'))
        carol = User(('Carol', 2, 1, '{}'))

        mock_users = [alice, bob, carol]

        mock_spoilers = [
            Spoiler(('test1', 'attach1', None, None)),
            Spoiler(('test2', 'attach2', None, None)),
        ]

        for user in mock_users:
            self.insert_user(user)

        for spoiler in mock_spoilers:
            self.insert_spoiler(spoiler)

        self.assertCountEqual(self.test_db.get_all_unnotified_users(), [alice, bob])

    #TODO: Split out into multiple tests
    def test_update_user(self):
        user = User(('Alice', 0, 0, '{}'))
        self.insert_user(user)
        self.assertEqual(self.test_db.get_user_from_id('Alice'), user)

        # last_updated
        user = User(('Bob', 0, 0, '{}'))
        self.insert_user(user)
        self.test_db.update_user('Bob', last_updated=10)
        user.last_updated = 10
        self.assertEqual(self.test_db.get_user_from_id('Bob'), user)

        # last_spoiled
        user = User(('Carol', 0, 0, '{}'))
        self.insert_user(user)
        self.test_db.update_user('Carol', last_spoiled=10)
        user.last_spoiled = 10
        self.assertEqual(self.test_db.get_user_from_id('Carol'), user)

        # options - update_mode, no previous update_mode
        user = User(('Dan', 0, 0, '{}'))
        self.insert_user(user)
        mock_options = {
            msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD
        }
        self.test_db.update_user('Dan', options=mock_options)
        user.options.update_mode = msbot.constants.POLL_MODE_CMD
        self.assertEqual(self.test_db.get_user_from_id('Dan'), user)

        # options - update_mode, existing update_mode
        mock_options = {
            msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD
        }
        user = User(('Erin', 0, 0, json.dumps(mock_options)))
        self.insert_user(user)
        mock_options = {
            msbot.constants.UPDATE_MODE: msbot.constants.ASAP_MODE_CMD
        }
        self.test_db.update_user('Erin', options=mock_options)
        user.options.update_mode = msbot.constants.ASAP_MODE_CMD
        self.assertEqual(self.test_db.get_user_from_id('Erin'), user)

    def test_spoiler_exists(self):
        test_spoiler = Spoiler(('test_spoiler_img', 0, None, 0))
        self.assertFalse(self.test_db.spoiler_exists(test_spoiler))
        self.insert_spoiler(test_spoiler)
        self.assertTrue(self.test_db.spoiler_exists(test_spoiler.image_url))

    def test_user_exists(self):
        test_user = 'test_user_id'
        self.assertFalse(self.test_db.user_exists(test_user))
        self.test_db.write(
            "INSERT INTO users VALUES('{test_user}', 0, 0, '{{}}')".format(test_user=test_user)
        )
        self.assertTrue(self.test_db.user_exists(test_user))

    def test_add_user(self):
        test_user = 'test_user_id'
        self.test_db.query(
            "SELECT id FROM users where id = '{test_user}'".format(test_user=test_user)
        )
        self.assertFalse(self.test_db.fetchall())

        self.test_db.add_user(test_user)

        self.test_db.query(
            "SELECT id FROM users where id = '{test_user}'".format(test_user=test_user)
        )
        self.assertTrue(self.test_db.fetchall())

    def test_delete_user(self):
        test_user = 'test_user_id'
        self.test_db.write(
            "INSERT INTO users VALUES('{test_user}', 0, 0, '{{}}')".format(test_user=test_user)
        )
        self.test_db.query(
            "SELECT id FROM users where id = '{test_user}'".format(test_user=test_user)
        )
        self.assertTrue(self.test_db.fetchall())

        self.test_db.delete_user(test_user)

        self.test_db.query(
            "SELECT id FROM users where id = '{test_user}'".format(test_user=test_user)
        )
        self.assertFalse(self.test_db.fetchall())

    def test_add_spoiler(self):
        test_spoiler = 'test_spoiler_img'
        test_attach_id = '12345'
        date = datetime.datetime.utcnow().date().strftime('%Y-%m-%d')
        self.test_db.query(
            "SELECT img FROM spoilers where img = '{test_spoiler}'"
            .format(test_spoiler=test_spoiler)
        )
        self.assertFalse(self.test_db.fetchall())

        self.test_db.add_spoiler(test_spoiler, test_attach_id)

        self.test_db.query(
            '''
            SELECT * FROM spoilers where img = '{test_spoiler}' AND
            attach_id = '{test_attach_id}'
            '''
            .format(
                test_spoiler=test_spoiler,
                test_attach_id=test_attach_id,
                date=date,
            )
        )

        self.assertTrue(self.test_db.fetchall())

    def test_get_latest_spoiler_id(self):
        self.test_db.add_spoiler('1', 0)
        self.test_db.add_spoiler('2', 0)
        self.test_db.add_spoiler('3', 0)
        self.test_db.add_spoiler('4', 0)

        self.assertEqual(self.test_db.get_latest_spoiler_id(), 4)

    def test_get_latest_spoiler_date(self):
        spoil1 = Spoiler(('test1', 'attach1', '2019-01-01', 1))
        spoil2 = Spoiler(('test2', 'attach2', '2019-01-02', 2))
        spoil3 = Spoiler(('test3', 'attach3', '2018-01-01', 3))

        mock_spoilers = [spoil1, spoil2, spoil3]

        for s in mock_spoilers:
            self.insert_spoiler(s)

        self.assertEqual(self.test_db.get_latest_spoiler_date(), '2019-01-02')


    def test_get_all_spoilers_on_date(self):
        spoil1 = Spoiler(('test1', 'attach1', '2019-01-01', 1))
        spoil2 = Spoiler(('test2', 'attach2', '2019-01-02', 2))
        spoil3 = Spoiler(('test3', 'attach3', '2019-01-02', 3))

        mock_spoilers = [spoil1, spoil2, spoil3]

        for s in mock_spoilers:
            self.insert_spoiler(s)

        self.assertCountEqual(
            self.test_db.get_all_spoilers_on_date('2019-01-02'),
            [spoil2, spoil3]
        )

    def test_get_all_spoilers(self):
        mock_spoilers = [
            Spoiler(('test1', 'attach1', '2019-01-01', 1)),
            Spoiler(('test2', 'attach2', '2019-01-01', 2)),
            Spoiler(('test3', 'attach3', '2019-01-01', 3)),
        ]
        for spoiler in mock_spoilers:
            self.insert_spoiler(spoiler)

        self.assertCountEqual(self.test_db.get_all_spoilers(), mock_spoilers)

    def test_get_spoilers_later_than(self):
        spoil1 = Spoiler(('test1', 'attach1', '2019-01-01', 1))
        spoil2 = Spoiler(('test2', 'attach2', '2019-01-01', 2))
        spoil3 = Spoiler(('test3', 'attach3', '2019-01-01', 3))
        mock_spoilers = [spoil1, spoil2, spoil3]
        for spoiler in mock_spoilers:
            self.insert_spoiler(spoiler)

        self.assertCountEqual(
            self.test_db.get_spoilers_later_than(1),
            [spoil2, spoil3]
        )

        self.assertCountEqual(
            self.test_db.get_spoilers_later_than(2),
            [spoil3]
        )

    def test_create_spoilers_table(self):
        self.test_db.write(
            'DROP TABLE IF EXISTS spoilers'
        )

        self.test_db.create_spoilers_table()

        self.test_db.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='spoilers'"
        )
        self.assertTrue(self.test_db.fetchall())

    def test_create_users_table(self):
        self.test_db.write(
            'DROP TABLE IF EXISTS users'
        )

        self.test_db.create_users_table()

        self.test_db.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        self.assertTrue(self.test_db.fetchall())

    def insert_user(self, user):
        self.test_db.write(
            ("INSERT INTO users VALUES('{mock_id}', {last_updated}, {last_spoiled}, '{options}')")
            .format(
                mock_id=user.user_id,
                last_updated=user.last_updated,
                last_spoiled=user.last_spoiled,
                options=user.options.to_json_string()
            )
        )

    def insert_spoiler(self, spoiler):
        spoiler_id = spoiler.spoiler_id if spoiler.spoiler_id != None else 'NULL'
        spoil_date = spoiler.date_spoiled if spoiler.date_spoiled != None else '2019-01-01'
        self.test_db.write(
            ("INSERT INTO spoilers VALUES('{mock_img}', "
             "'{mock_attach_id}', '{mock_date}', {mock_spoil_id})")
            .format(
                mock_img=spoiler.image_url,
                mock_attach_id=spoiler.attach_id,
                mock_date=spoiler.date_spoiled,
                mock_spoil_id=spoiler_id
            )
        )
