import json
import unittest

import unittest.mock as mock

from boddle import boddle

import webhook

TEST_ACCESS_TOKEN = 'TEST_ACCESS_TOKEN'
TEST_VERIFY_TOKEN = 'TEST_VERIFY_TOKEN'
TEST_API_KEY = 'TEST_API_KEY'


class TestWebhook(unittest.TestCase):
    def setUp(self):
        settings_patch = mock.patch('webhook.msbot.settings')
        self.addCleanup(settings_patch.stop)
        self.settings_mock = settings_patch.start()
        self.settings_mock.configure_mock(
            **{
                'PAGE_ACCESS_TOKEN': TEST_ACCESS_TOKEN,
                'VERIFY_TOKEN': TEST_VERIFY_TOKEN,
                'API_KEY': TEST_API_KEY,
            }
        )

        requests_patch = mock.patch('webhook.requests')
        self.addCleanup(requests_patch.stop)
        self.requests_mock = requests_patch.start()

    def test_send_message(self):
        mock_send_psid = 123456
        mock_message = 'Hello'
        mock_request_body = {
            'json': {
                webhook.RECIPIENT: {
                    webhook.ID: mock_send_psid
                },
                webhook.MESSAGE: mock_message
            },
            'params': {
                webhook.ACCESS_TOKEN: TEST_ACCESS_TOKEN,
                webhook.RECIPIENT: mock_send_psid
            }
        }

        webhook.send_message(mock_send_psid, mock_message)

        self.requests_mock.post.assert_called_once()

        _, request_body = self.requests_mock.post.call_args

        self.assertDictEqual(request_body, mock_request_body)

    def test_webhook_event_text_message_received(self):
        with boddle(
            body=json.dumps(
                {
                    webhook.OBJECT: webhook.PAGE_OBJECT,
                    webhook.ENTRY: [
                        {
                            webhook.MESSAGING: [
                                {
                                    webhook.MESSAGE: {
                                        webhook.TEXT: 'Hello!'
                                    },
                                    webhook.SENDER: {
                                        webhook.ID: 123456
                                    }
                                }
                            ],
                        }
                    ]
                }
            )
        ):
            webhook.webhook_event()
            self.assertEqual(webhook.response.status_code, 200)

    def test_webhook_event_non_text_message_received(self):
        with boddle(
            body=json.dumps(
                {
                    webhook.OBJECT: webhook.PAGE_OBJECT,
                    webhook.ENTRY: [
                        {
                            webhook.MESSAGING: [
                                {
                                    webhook.MESSAGE: {
                                        'foo': None
                                    },
                                    webhook.SENDER: {
                                        webhook.ID: 123456
                                    }
                                }
                            ],
                        }
                    ]
                }
            )
        ):
            webhook.webhook_event()
            self.assertEqual(webhook.response.status_code, 200)

    def test_webhook_event_no_page_object(self):
        with boddle(
            body=json.dumps(
                {
                    webhook.OBJECT: None,
                }
            )
        ):
            webhook.webhook_event()
            self.assertEqual(webhook.response.status_code, 404)

    def test_webhook_verify_success(self):
        with boddle(
            query={
                webhook.MODE: webhook.SUBSCRIBE,
                webhook.TOKEN: TEST_VERIFY_TOKEN,
                webhook.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), 'TEST_CHALLENGE')
            self.assertEqual(webhook.response.status_code, 200)

    def test_webhook_verify_bad_token(self):
        with boddle(
            query={
                webhook.MODE: webhook.SUBSCRIBE,
                webhook.TOKEN: 'BAD_TOKEN',
                webhook.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            webhook.webhook_verify()
            self.assertEqual(webhook.response.status_code, 403)

    def test_webhook_verify_bad_mode(self):
        with boddle(
            query={
                webhook.MODE: 'BAD_MODE',
                webhook.TOKEN: TEST_VERIFY_TOKEN,
                webhook.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            webhook.webhook_verify()
            self.assertEqual(webhook.response.status_code, 403)

    def test_webhook_verify_no_mode(self):
        with boddle(
            query={
                webhook.MODE: None,
                webhook.TOKEN: TEST_VERIFY_TOKEN,
                webhook.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), None)

    def test_webhook_verify_no_token(self):
        with boddle(
            query={
                webhook.MODE: webhook.SUBSCRIBE,
                webhook.TOKEN: None,
                webhook.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), None)
