import json
import unittest

import unittest.mock as mock

import msbot.mslib as mslib

TEST_ACCESS_TOKEN = 'TEST_ACCESS_TOKEN'
TEST_VERIFY_TOKEN = 'TEST_VERIFY_TOKEN'
TEST_API_KEY = 'TEST_API_KEY'


class TestMSLib(unittest.TestCase):
    def setUp(self):
        settings_patch = mock.patch('msbot.settings')
        self.addCleanup(settings_patch.stop)
        self.settings_mock = settings_patch.start()
        self.settings_mock.configure_mock(
            **{
                'PAGE_ACCESS_TOKEN': TEST_ACCESS_TOKEN,
                'VERIFY_TOKEN': TEST_VERIFY_TOKEN,
                'API_KEY': TEST_API_KEY,
            }
        )

    @mock.patch('msbot.mslib.requests.get')
    def test_getLatestSpoilers(self, get_mock):
        mock_spoilers = {
            'item': [
                {
                    'cardUrl': 'a.jpg'
                },
                {
                    'cardUrl': 'b.jpg'
                }
            ]
        }
        get_mock.return_value = mock.Mock(
            text='(' + json.dumps(mock_spoilers) + ')'
        )

        latest_spoils = mslib.getLatestSpoilers()

        self.assertEqual(
            latest_spoils,
            [
                'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/a.jpg',
                'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/b.jpg',
            ]
        )

    @mock.patch('msbot.mslib.requests.get')
    def test_getLatestSpoilers_ignores_bad_values(self, get_mock):
        mock_spoilers = {
            'item': [
                {
                    'cardUrl': 'poopybutt'
                },
                {
                    'cardUrl': 'b.jpg'
                }
            ]
        }
        get_mock.return_value = mock.Mock(
            text='(' + json.dumps(mock_spoilers) + ')'
        )

        latest_spoils = mslib.getLatestSpoilers()

        self.assertEqual(
            latest_spoils,
            [
                'http://mythicspoilerapi.dungeonmastering.net/card_images/new_spoils/b.jpg',
            ]
        )
