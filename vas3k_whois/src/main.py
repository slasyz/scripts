import logging
import os.path
import time

import yaml
import requests
from telegram.client import Telegram


config_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config.yml')
tdlib_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../tdlib_files/')


def main():
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    with open(config_filename, 'r') as f:
        config = yaml.safe_load(f)

    tg = Telegram(
        api_id=config['api_id'],
        api_hash=config['api_hash'],
        phone=config['phone'],
        database_encryption_key=config['database_encryption_key'],
        files_directory=tdlib_dir,
    )
    chats = config['chats']
    logging.info(f'-> chats: {chats}\n')

    tg.login()

    def new_message_handler(update):
        message = update['message']
        # print(message)

        if 'sender_id' in message.keys():
            sender_id = message['sender_id']
            if 'user_id' in sender_id.keys():
                if sender_id['user_id'] == config['owner_user_id']:
                    requests.get(config['uptime_url'])
                    logging.info('-> got message from owner: %s\n', message)

        logging.info('-> queue size: %d of %d', tg.worker._queue.qsize(), tg.worker._queue.maxsize)
        if tg.worker._queue.qsize() >= 500:
            requests.get(config['uptime_too_big_url'] % (tg.worker._queue.qsize(),))

        # message = {
        #     '@type': 'message',
        #     'id': 627300000000,
        #     'sender_id': {
        #         '@type': 'messageSenderUser', 'user_id': 123123123
        #     },
        #     'chat_id': -650020081, 'is_outgoing': False, 'is_pinned': False, 'can_be_edited': False,
        #     'can_be_forwarded': False, 'can_be_saved': True, 'can_be_deleted_only_for_self': True,
        #     'can_be_deleted_for_all_users': True, 'can_get_added_reactions': False, 'can_get_statistics': False,
        #     'can_get_message_thread': False, 'can_get_viewers': False, 'can_get_media_timestamp_links': False,
        #     'has_timestamped_media': True, 'is_channel_post': False, 'contains_unread_mention': False,
        #     'date': 1669563691, 'edit_date': 0, 'unread_reactions': [], 'reply_in_chat_id': 0,
        #     'reply_to_message_id': 0, 'message_thread_id': 0, 'ttl': 0, 'ttl_expires_in': 0.0, 'via_bot_user_id': 0,
        #     'author_signature': '', 'media_album_id': '0', 'restriction_reason': '',
        #     'content': {
        #         '@type': 'messageChatJoinByLink'
        #     }
        # }
        #
        # message = {
        #     '@type': 'message',
        #     'id': 627300000000,
        #     'sender_id': {
        #         '@type': 'messageSenderUser', 'user_id': 123123
        #     },
        #     'chat_id': -650020081, 'is_outgoing': True, 'is_pinned': False, 'can_be_edited': False,
        #     'can_be_forwarded': False, 'can_be_saved': True, 'can_be_deleted_only_for_self': True,
        #     'can_be_deleted_for_all_users': True, 'can_get_added_reactions': False, 'can_get_statistics': False,
        #     'can_get_message_thread': False, 'can_get_viewers': True, 'can_get_media_timestamp_links': False,
        #     'has_timestamped_media': True, 'is_channel_post': False, 'contains_unread_mention': False,
        #     'date': 1669564406, 'edit_date': 0, 'unread_reactions': [], 'reply_in_chat_id': 0,
        #     'reply_to_message_id': 0, 'message_thread_id': 0, 'ttl': 0, 'ttl_expires_in': 0.0, 'via_bot_user_id': 0,
        #     'author_signature': '', 'media_album_id': '0', 'restriction_reason': '',
        #     'content': {
        #         '@type': 'messageChatAddMembers', 'member_user_ids': [123123123]
        #     }
        # }

        if message['@type'] != 'message':
            return
        if 'content' not in message.keys():
            logging.info('-> received message without content: %s\n', message)
            return

        content_type = message['content']['@type']
        if content_type not in ('messageChatJoinByLink', 'messageChatAddMembers'):
            return

        # Logging only join/invite messages
        chat_id = message['chat_id']
        logging.info('-> received message in %d: %s\n', chat_id, message)

        if chat_id not in chats:
            return

        # Now we have a join/invite message in one of enabled chats
        # Sending a /whois reply to it

        message_id = message['id']
        logging.info('-> replying to message %d in chat %d\n', message_id, chat_id)
        data = {
            '@type': 'sendMessage',
            'chat_id': chat_id,
            'reply_to_message_id': message_id,
            'input_message_content': {
                '@type': 'inputMessageText',
                'text': {'@type': 'formattedText', 'text': '/whois'},
            },
        }

        # Yes, calling a protected method.  And there's nothing you can do about it.
        res = tg._send_data(data)
        logging.info('-> sending %s\n', data)
        res.wait()

        # res.update = {
        #     '@type': 'message',
        #     'id': 18874369,
        #     'sender_id': {'@type': 'messageSenderUser', 'user_id': 59352582},
        #     'chat_id': -1001550504221, 'sending_state': {
        #         '@type': 'messageSendingStatePending'
        #     },
        #     'is_outgoing': True, 'is_pinned': False, 'can_be_edited': False, 'can_be_forwarded': True,
        #     'can_be_saved': True, 'can_be_deleted_only_for_self': False, 'can_be_deleted_for_all_users': True,
        #     'can_get_added_reactions': False, 'can_get_statistics': False, 'can_get_message_thread': False,
        #     'can_get_viewers': False, 'can_get_media_timestamp_links': False, 'has_timestamped_media': False,
        #     'is_channel_post': False, 'contains_unread_mention': False, 'date': 1669566335, 'edit_date': 0,
        #     'unread_reactions': [], 'reply_in_chat_id': -1001550504221, 'reply_to_message_id': 18874368,
        #     'message_thread_id': 0, 'ttl': 0, 'ttl_expires_in': 0.0, 'via_bot_user_id': 0, 'author_signature': '',
        #     'media_album_id': '0', 'restriction_reason': '',
        #     'content': {
        #         '@type': 'messageText',
        #         'text': {
        #             '@type': 'formattedText', 'text': '/whois', 'entities': []
        #         }
        #     },
        #     '@extra': {
        #         'request_id': '7775544792594365acb255e09c6cfdf4'
        #     }
        # }
        logging.info('-> sent. Got this: %s\n', res.update)
        outgoing_message_id = res.update['id']
        time.sleep(0.21)
        tg.delete_messages(chat_id, [outgoing_message_id])
        return

    tg.add_message_handler(new_message_handler)
    tg.idle()  # blocking waiting for CTRL+C


if __name__ == '__main__':
    main()
