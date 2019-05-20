import json
import unittest

import unittest.mock as mock

from boddle import boddle

import webhook

import msbot.constants
from msbot.spoiler import Spoiler
from msbot.user import User

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

        db_patch = mock.patch('msbot.msdb.MSDatabase')
        self.addCleanup(db_patch.stop)
        self.mock_db = db_patch.start()
        self.db_mock = self.mock_db.return_value

    def test_send_message(self):
        mock_send_psid = 123456
        mock_message = 'Hello'
        mock_request_body = {
            'json': {
                msbot.constants.RECIPIENT: {
                    msbot.constants.ID: mock_send_psid
                },
                msbot.constants.MESSAGE: mock_message
            },
            'params': {
                msbot.constants.ACCESS_TOKEN: TEST_ACCESS_TOKEN,
                msbot.constants.RECIPIENT: mock_send_psid
            }
        }

        webhook.send_message(mock_send_psid, mock_message)

        self.assertEqual(self.requests_mock.post.call_count, 1)

        _, request_body = self.requests_mock.post.call_args

        self.assertDictEqual(request_body, mock_request_body)

    def test_to_text_response(self):
        text = 'test_text'
        self.assertDictEqual(
            webhook.to_text_response(text),
            {
                msbot.constants.TEXT: text
            }
        )

    def test_create_quick_reply_button(self):
        payload = 'test_payload'
        self.assertDictEqual(
            webhook.create_quick_reply_button(payload),
            {
                msbot.constants.CONTENT_TYPE: msbot.constants.TEXT,
                msbot.constants.TITLE: payload.capitalize(),
                msbot.constants.PAYLOAD: payload,
            }
        )

    def test_text_quick_reply_response(self):
        text = 'test_text'
        buttons = [
            webhook.create_quick_reply_button('test1'),
            webhook.create_quick_reply_button('test2'),
            webhook.create_quick_reply_button('test3'),
        ]

        self.assertDictEqual(
            webhook.text_quick_reply_response(text, buttons),
            {
                msbot.constants.TEXT: text,
                msbot.constants.QUICK_REPLIES: buttons,
            }
        )

    def test_get_attach_id_for(self):
        test_url = 'www.fake.com'
        attach_id = 123456
        response_mock = mock.Mock()
        response_mock.text = json.dumps({'attachment_id': attach_id})

        self.requests_mock.post.return_value = response_mock
        self.assertEqual(webhook.get_attach_id_for(test_url), attach_id)

    @mock.patch('webhook.send_message')
    def test_send_spoiler_to(self, send_mock):
        test_user = User((1234, 0, 0, '{}'))
        test_spoiler = Spoiler(('test', 123456, '2019-01-01', None))

        test_response = {
            'attachment': {
                'type': 'image',
                'payload': {
                    'attachment_id': test_spoiler.attach_id
                }
            }
        }

        webhook.send_spoiler_to(test_user, test_spoiler)

        send_mock.assert_called_once_with(test_user.user_id, test_response)


    @mock.patch('webhook.get_attach_id_for')
    @mock.patch('msbot.mslib.getLatestSpoilers')
    def test_update_spoilers(self, spoils_mock, attach_mock):
        test_spoilers = {
            '1': {'exists': False, 'attach_id': '123'},
            '2': {'exists': False, 'attach_id': '456'},
            '3': {'exists': True, 'attach_id': '789'},
        }

        def spoiler_exists_return_values(spoiler):
            return test_spoilers[spoiler]['exists']

        def get_attach_id_for_return_values(spoiler):
            return test_spoilers[spoiler]['attach_id']

        self.db_mock.spoiler_exists.side_effect = spoiler_exists_return_values

        spoils_mock.return_value = [k for k in test_spoilers.keys()]

        attach_mock.side_effect = get_attach_id_for_return_values

        webhook.update_spoilers()

        calls = [
            mock.call('2', '456'),
            mock.call('1', '123'),
        ]

        self.db_mock.add_spoiler.assert_has_calls(calls, any_order=True)
        self.assertEqual(self.db_mock.add_spoiler.call_count, len(calls))

    @mock.patch('webhook.handle_message')
    @mock.patch('webhook.send_update')
    def test_update_user(self, send_mock, handle_mock):

        # default user
        alice = User(('Alice', 0, 0, '{}'))
        self.db_mock.get_latest_spoiler_id.return_value = 2
        webhook.update_user(alice)
        send_mock.assert_called_once_with(alice.user_id,
                                          msbot.constants.RESP_UPDATE
                                          .format(num_spoilers=2)
                                          )

        # asap user
        alice.options.update_mode = msbot.constants.ASAP_MODE_CMD
        webhook.update_user(alice)
        handle_mock.assert_called_once_with(alice.user_id,
                                            msbot.constants.SEND_CMD)

        # unsupported mode
        send_mock.reset_mock()
        alice = User(('Alice', 0, 0, '{}'))
        self.db_mock.get_latest_spoiler_id.return_value = 2
        alice.options.update_mode = 'UNSUPPORTED'
        webhook.update_user(alice)
        send_mock.assert_called_once_with(alice.user_id,
                                          msbot.constants.RESP_UPDATE
                                          .format(num_spoilers=2)
                                          )


    @mock.patch('webhook.send_update')
    def test_update_users(self, send_mock):

        alice = User(('Alice', 0, 0, '{}'))
        bob = User(('Bob', 4, 1, '{}'))
        dan = User(('Dan', 3, 3, '{}'))

        self.db_mock.get_all_unnotified_users.return_value = [alice, bob]

        self.db_mock.get_latest_spoiler_id.return_value = 5

        calls = [
            mock.call(alice.user_id,
                      msbot.constants.RESP_UPDATE.format(num_spoilers=5)),
            mock.call(bob.user_id,
                      msbot.constants.RESP_UPDATE.format(num_spoilers=4)),
        ]

        webhook.update_users()

        send_mock.assert_has_calls(calls, any_order=True)
        self.assertEqual(send_mock.call_count, len(calls))

    @mock.patch('webhook.send_message')
    def test_handle_message_sub_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.HELLO_CMD)
        self.db_mock.add_user.assert_called_once_with(sender_psid)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.text_quick_reply_response(
                msbot.constants.RESP_SUBBED,
                [ webhook.INFO_BUTTON ]
            )
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_sub_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.HELLO_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(msbot.constants.RESP_ALREADY_SUBBED)
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_unsub_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.GOODBYE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(msbot.constants.RESP_ALREADY_UNSUBBED)
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_unsub_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.GOODBYE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(msbot.constants.RESP_UNSUBBED)
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_send_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.SEND_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    @mock.patch('webhook.send_spoiler_to')
    def test_handle_message_send_when_subbed(self, spoil_mock, send_mock):
        alice = User(('Alice', 5, 5, '{}'))
        spoiler1 = Spoiler(('spoil1','attach1','2019-01-01',None))
        spoiler2 = Spoiler(('spoil2','attach2','2019-01-01',None))
        spoiler3 = Spoiler(('spoil3','attach3','2019-01-01',None))
        self.db_mock.user_exists.return_value = True
        self.db_mock.get_user_from_id.return_value = User(('Alice', 5, 5, '{}'))
        latest_spoiler = 8
        self.db_mock.get_latest_spoiler_id.return_value = latest_spoiler
        self.db_mock.get_spoilers_later_than.return_value = []
        sender_psid = 1234

        # no new spoilers
        webhook.handle_message(sender_psid, msbot.constants.SEND_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.text_quick_reply_response(
                msbot.constants.RESP_UPDATE_UPDATED,
                [ webhook.RECENT_BUTTON ]

            )
        )

        # new spoilers
        send_mock.reset_mock()
        self.db_mock.get_spoilers_later_than.return_value = [
            spoiler1,
            spoiler2,
            spoiler3,
        ]
        webhook.handle_message(sender_psid, msbot.constants.SEND_CMD)
        calls = [
            mock.call(alice, spoiler1),
            mock.call(alice, spoiler2),
            mock.call(alice, spoiler3),
        ]
        spoil_mock.assert_has_calls(calls, any_order=True)
        self.assertEqual(spoil_mock.call_count, len(calls))
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(
                msbot.constants.RESP_UPDATE_COMPLETE
            )
        )
        self.db_mock.update_user.called_once_with(alice.user_id, latest_spoiler)

    @mock.patch('webhook.send_message')
    def test_handle_message_recent_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.RECENT_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    @mock.patch('webhook.send_spoiler_to')
    def test_handle_message_recent_when_subbed(self, spoil_mock, send_mock):
        alice = User(('Alice', 8, 8, '{}'))
        latest_date = '2019-02-02'
        spoiler1 = Spoiler(('spoil1','attach1', latest_date, None))
        spoiler2 = Spoiler(('spoil2','attach2', latest_date, None))

        self.db_mock.user_exists.return_value = True
        self.db_mock.get_user_from_id.return_value = User(('Alice', 8, 8, '{}'))

        latest_spoiler = 8
        self.db_mock.get_latest_spoiler_id.return_value = latest_spoiler
        self.db_mock.get_latest_spoiler_date.return_value = latest_date
        self.db_mock.get_all_spoilers_on_date.return_value = [
            spoiler1,
            spoiler2,
        ]

        sender_psid = 1234

        # new spoilers
        webhook.handle_message(sender_psid, msbot.constants.RECENT_CMD)
        calls = [
            mock.call(alice, spoiler1),
            mock.call(alice, spoiler2),
        ]

        spoil_mock.assert_has_calls(calls, any_order=True)
        self.assertEqual(spoil_mock.call_count, len(calls))
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(
                msbot.constants.RESP_LAST_SPOILER_INFO.format(date_string=latest_date)
            )
        )
        self.db_mock.update_user.called_once_with(alice.user_id,
                                        latest_spoiler,
                                        latest_spoiler
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_mode_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.MODE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_mode_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        self.db_mock.get_user_from_id.return_value = User(
            ('Alice',
             0,
             0,
             json.dumps(
                 {
                     msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD
                 }
             )
            )
        )

        text = msbot.constants.RESP_MODE_PROMPT.format(
            update_mode = msbot.constants.POLL_MODE_CMD
        )

        webhook.handle_message(sender_psid, msbot.constants.MODE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.text_quick_reply_response(text, webhook.UPDATE_MODE_BUTTONS)
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_poll_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.POLL_MODE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_poll_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.POLL_MODE_CMD)
        self.db_mock.update_user.called_once_with(
            sender_psid,
            options={
                msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD
            }
        )
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(
                msbot.constants.RESP_MODE_COMPLETE.format(
                    update_mode=msbot.constants.POLL_MODE_CMD
                )
            )
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_asap_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.ASAP_MODE_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_asap_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.ASAP_MODE_CMD)
        self.db_mock.update_user.called_once_with(
            sender_psid,
            options={
                msbot.constants.UPDATE_MODE: msbot.constants.ASAP_MODE_CMD
            }
        )
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.to_text_response(
                msbot.constants.RESP_MODE_COMPLETE.format(
                    update_mode=msbot.constants.ASAP_MODE_CMD
                )
            )
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_info_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.INFO_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_info_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, msbot.constants.INFO_CMD)
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.text_quick_reply_response(
                msbot.constants.RESP_INFO_PROMPT,
                webhook.INFO_PROMPT_BUTTONS
            )
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_invalid_when_subbed(self, send_mock):
        self.db_mock.user_exists.return_value = True
        sender_psid = 1234

        webhook.handle_message(sender_psid, 'unsupported_message')
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.text_quick_reply_response(
                msbot.constants.RESP_INVALID_SUBBED,
                [ webhook.INFO_BUTTON ]
            )
        )

    @mock.patch('webhook.send_message')
    def test_handle_message_invalid_when_unsubbed(self, send_mock):
        self.db_mock.user_exists.return_value = False
        sender_psid = 1234

        webhook.handle_message(sender_psid, 'unsupported_message')
        send_mock.assert_called_once_with(
            sender_psid,
            webhook.RESP_INVALID_CMD
        )

    def test_is_allowed_psid_dev_mode_off(self):
        self.settings_mock.configure_mock(
            **{
                'DEV_MODE': False,
                'DEV_SAFELIST': {},
            }
        )
        self.assertTrue(webhook.is_allowed_psid('1234'))

    def test_is_allowed_psid_dev_mode_on(self):
        self.settings_mock.configure_mock(
            **{
                'DEV_MODE': True,
                'DEV_SAFELIST': {},
            }
        )
        self.assertFalse(webhook.is_allowed_psid('1234'))

        self.settings_mock.configure_mock(
            **{
                'DEV_MODE': True,
                'DEV_SAFELIST': {'1234'},
            }
        )
        self.assertTrue(webhook.is_allowed_psid('1234'))

    def test_webhook_event_text_message_received(self):
        with boddle(
            body=json.dumps(
                {
                    msbot.constants.OBJECT: msbot.constants.PAGE_OBJECT,
                    msbot.constants.ENTRY: [
                        {
                            msbot.constants.MESSAGING: [
                                {
                                    msbot.constants.MESSAGE: {
                                        msbot.constants.TEXT: 'Hello!'
                                    },
                                    msbot.constants.SENDER: {
                                        msbot.constants.ID: 123456
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
                    msbot.constants.OBJECT: msbot.constants.PAGE_OBJECT,
                    msbot.constants.ENTRY: [
                        {
                            msbot.constants.MESSAGING: [
                                {
                                    msbot.constants.MESSAGE: {
                                        'foo': None
                                    },
                                    msbot.constants.SENDER: {
                                        msbot.constants.ID: 123456
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
                    msbot.constants.OBJECT: None,
                }
            )
        ):
            webhook.webhook_event()
            self.assertEqual(webhook.response.status_code, 404)

    def test_webhook_verify_success(self):
        with boddle(
            query={
                msbot.constants.MODE: msbot.constants.SUBSCRIBE,
                msbot.constants.TOKEN: TEST_VERIFY_TOKEN,
                msbot.constants.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), 'TEST_CHALLENGE')
            self.assertEqual(webhook.response.status_code, 200)

    def test_webhook_verify_bad_token(self):
        with boddle(
            query={
                msbot.constants.MODE: msbot.constants.SUBSCRIBE,
                msbot.constants.TOKEN: 'BAD_TOKEN',
                msbot.constants.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            webhook.webhook_verify()
            self.assertEqual(webhook.response.status_code, 403)

    def test_webhook_verify_bad_mode(self):
        with boddle(
            query={
                msbot.constants.MODE: 'BAD_MODE',
                msbot.constants.TOKEN: TEST_VERIFY_TOKEN,
                msbot.constants.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            webhook.webhook_verify()
            self.assertEqual(webhook.response.status_code, 403)

    def test_webhook_verify_no_mode(self):
        with boddle(
            query={
                msbot.constants.MODE: None,
                msbot.constants.TOKEN: TEST_VERIFY_TOKEN,
                msbot.constants.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), None)

    def test_webhook_verify_no_token(self):
        with boddle(
            query={
                msbot.constants.MODE: msbot.constants.SUBSCRIBE,
                msbot.constants.TOKEN: None,
                msbot.constants.CHALLENGE: 'TEST_CHALLENGE'
            }
        ):
            self.assertEqual(webhook.webhook_verify(), None)
