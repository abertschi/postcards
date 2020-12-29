#!/usr/bin/env python
# encoding: utf-8

import sys
import logging
from postcard_creator import postcard_creator
import base64
import json
import os
import argparse
from argparse import RawTextHelpFormatter
import urllib
import inflection
import random
import pkg_resources
from postcards import __version__
from postcard_creator import __version__ as postcard_creator_version

LOGGING_TRACE_LVL = 5
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(name)s (%(levelname)s): %(message)s')

# logging.basicConfig(stream=sys.stdout, level=logging.INFO,
#                     format='%(asctime)s %(name)s (%(levelname)s): %(message)s')

DEFAULT_KEY = 'olMcxzq9Cq5lJpsoh4FvPKU'


class Postcards:
    def __init__(self, logger=None):
        self.logger = self._create_logger(logger)
        self.default_key = DEFAULT_KEY
        try:
            self.default_key = os.environ['POSTCARDS_KEY']
        except KeyError:
            pass

    def main(self, argv):
        parser = self._build_root_parser(argv)
        subparsers = parser.add_subparsers(help='', dest='mode')
        self._build_subparser_generate(subparsers)
        self._build_subparser_send(subparsers)
        self._build_subparser_encrypt(subparsers)
        self._build_subparser_decrypt(subparsers)
        self.build_plugin_subparser(subparsers)
        self.logger.trace(argv)
        args = parser.parse_args()
        self._configure_logging(self.logger, args.verbose_count)
        self.logger.info(f'postcards {__version__} with postcard-creator {postcard_creator_version}')
        self.logger.debug(args)

        if args.mode == 'generate':
            self.do_command_generate(args)
        elif args.mode == 'send':
            self.do_command_send(args)
        elif args.mode == 'encrypt':
            self.do_command_encrypt(args)
        elif args.mode == 'decrypt':
            self.do_command_decrypt(args)
        elif self.can_handle_command(args.mode):
            self.handle_command(args.mode, args)
        else:
            parser.print_usage()

    def do_command_generate(self, args):
        target_location = str(os.path.join(os.getcwd(), 'config.json'))

        if os.path.isfile(target_location):
            self.logger.error('config file already exist in current directory.')
            exit(1)

        content = pkg_resources.resource_string(__name__, 'template_config.json').decode('utf-8')
        file = open(target_location, 'w')
        file.write(content)
        file.close()

        self.logger.info('empty config file generated at {}'.format(target_location))

    def do_command_encrypt(self, args):
        self.encrypt_credential(args.key, args.credential)

    def do_command_decrypt(self, args):
        self.decrypt_credential(args.key, args.credential)

    def do_command_send(self, args):
        config = self._read_json_file(args.config_file[0], 'config')

        if args.accounts_file:
            accounts_file = self._read_json_file(args.accounts_file, 'accounts')

        key_settings = self._parse_key(args)
        accounts = self._get_accounts(config=accounts_file if args.accounts_file else config,
                                      key=key_settings['key'] if key_settings['uses_key'] else None,
                                      username=args.username,
                                      password=args.password)
        random.shuffle(accounts)
        self._validate_config(config, accounts)

        plugin_payload = config.get('payload')
        if args and args.test_plugin:
            self.test_plugin_and_stop(plugin_payload, args)

        self.logger.info('checking for valid accounts')
        wrappers, try_again_after = self._create_pcc_wrappers(accounts,
                                                              stop_on_first_valid=not args.all_accounts)
        if not wrappers:
            self.logger.error('no valid account given. try again after {}'.format(try_again_after))
            exit(1)

        self.send_cards(pcc_wrappers=wrappers,
                        recipient=config.get('recipient'),
                        sender=config.get('sender') if config.get('sender') else config.get('recipient'),
                        mock=bool(args.mock),
                        plugin_payload=plugin_payload,
                        picture_stream=self._read_picture(args.picture) if args.picture else None,
                        message=self._handle_message_argument(args.message),
                        cli_args=args)

    def send_cards(self, pcc_wrappers, recipient, sender, mock=False, plugin_payload={},
                   message=None, picture_stream=None, cli_args={}):

        for wrapper in pcc_wrappers:
            self.send_card(wrapper, recipient, sender,
                           mock=mock, plugin_payload=plugin_payload,
                           message=message, picture_stream=picture_stream,
                           cli_args=cli_args)

    def send_card(self, pcc_wrapper, recipient, sender, mock=False, plugin_payload=None,
                  message=None, picture_stream=None, cli_args={}):

        if self._is_plugin():
            img_and_text = self.get_img_and_text(plugin_payload, cli_args=cli_args if cli_args else {})

            if not message:
                message = img_and_text['text']
            if not picture_stream:
                picture_stream = img_and_text['img']

        card = postcard_creator.Postcard(message=message,
                                         recipient=self._create_recipient(recipient),
                                         sender=self._create_sender(sender),
                                         picture_stream=picture_stream)

        self.logger.info('uploading postcard to server')
        try:
            self.delegate_send_free_card(pcc_wrapper, card, mock_send=mock)
        except Exception as e:
            self.logger.fatal('can not send postcard: ' + str(e))
            raise e

        if mock:
            self.logger.info('postcard not sent because of mock=True')
        else:
            self.logger.info('postcard is successfully sent')

    def delegate_send_free_card(self, pcc_wrapper, postcard, mock_send):
        pcc_wrapper.send_free_card(postcard=postcard, mock_send=mock_send)

    def encrypt_credential(self, key, credential):
        self.logger.info('encrypted credential:')
        self.logger.info(self._encrypt(key, credential))

    def decrypt_credential(self, key, credential):
        self.logger.info('decrypted credential:')
        self.logger.info(self._decrypt(key, credential))

    def test_plugin_and_stop(self, payload={}, args={}):
        self.logger.info('running plugin only (--test-plugin)')
        self.get_img_and_text(payload, cli_args=args)
        exit(0)

    def _create_pcc_wrappers(self, accounts, stop_on_first_valid=True):
        pcc_wrappers = []
        try_again_after = ''

        for account in accounts:
            token = postcard_creator.Token()
            if token.has_valid_credentials(account.get('username'), account.get('password')):
                pcc = postcard_creator.PostcardCreator(token)
                if pcc.has_free_postcard():
                    pcc_wrappers.append(pcc)
                    self.logger.info('account {} is valid'.format(account.get("username")))
                    if stop_on_first_valid:
                        break
                else:
                    next_quota = pcc.get_quota().get('next')
                    if next_quota < try_again_after or try_again_after == '':
                        try_again_after = next_quota

                    self.logger.debug('account {} is invalid. '.format(account.get("username")) +
                                      'new quota available after {}.'.format(next_quota))
            else:
                self.logger.warning('wrong user credentials '
                                    'for {}'.format(account.get("username")))

        return pcc_wrappers, try_again_after

    def _create_recipient(self, recipient):
        return postcard_creator.Recipient(prename=recipient.get('firstname'),
                                          lastname=recipient.get('lastname'),
                                          street=recipient.get('street'),
                                          zip_code=recipient.get('zipcode'),
                                          place=recipient.get('city'),
                                         salutation=recipient.get('salutation') if recipient.get('salutation') else '')

    def _create_sender(self, sender):
        return postcard_creator.Sender(prename=sender.get('firstname'),
                                       lastname=sender.get('lastname'),
                                       street=sender.get('street'),
                                       zip_code=sender.get('zipcode'),
                                       place=sender.get('city'))

    def _get_accounts(self, config, key=None, username=None, password=None):
        accounts = []
        if username and password:
            self.logger.debug('using command line args as username and password')
            accounts.append({
                'username': username,
                'password': password
            })
        else:
            for account in config.get('accounts'):
                accounts.append({
                    'username': account.get('username'),
                    'password': account.get('password') if not key else self._decrypt(key, account.get('password'))
                })
        return accounts

    def _parse_key(self, args):
        key = self.default_key
        uses_key = True

        if isinstance(args.key, tuple):
            uses_key = False
            self.logger.debug('using no key')
        elif args.key is None:
            key = self.default_key
            self.logger.debug('using default key')
        else:
            key = args.key
            self.logger.debug('using custom key')
        return {
            'uses_key': uses_key,
            'key': key
        }

    def _validate_config(self, config, accounts):
        if not accounts:
            self.logger.error('no account set in config/accounts file')
            exit(1)

        if not config.get('recipient'):
            self.logger.error('no recipient sent in config file')
            exit(1)

        recipient = config.get('recipient')
        required = ['firstname', 'lastname', 'street', 'zipcode', 'city']
        if not all(recipient.get(field) for field in required):
            self.logger.error('recipient is invalid. required fields are ' + str(required))
            exit(1)

        sender = config.get('sender')
        if sender:
            if not all(sender.get(field) for field in required):
                self.logger.error('sender is invalid. required fields are ' + str(required))
                exit(1)

    def _read_json_file(self, location, name):
        location = self._make_absolute_path(location)
        self.logger.info('reading {} file at {}'.format(name, location))

        if not os.path.isfile(location):
            self.logger.fatal('{} file not found at {}'.format(name, location))
            exit(1)
        try:
            with open(location) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error('can not parse {} file {} . is it valid json ?'.format(name, location))
            exit(1)

    def _read_picture(self, location):
        if location.startswith('http'):
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) ' +
                              'Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'
            }
            self.logger.debug('reading picture from the internet at ' + location)
            request = urllib.request.Request(location, None, headers)
            return urllib.request.urlopen(request)
        else:
            location = self._make_absolute_path(location)
            self.logger.debug('reading picture from ' + location)
            if not os.path.isfile(location):
                self.logger.error('picture not found at ' + location)
                exit(1)
            return open(location, 'rb')

    def _make_absolute_path(self, path):
        if os.path.isabs(path):
            return path
        else:
            return str(os.path.join(os.getcwd(), path))

    def _encrypt(self, key, msg):
        return self._encode(key.encode('utf-8'), msg.encode('utf-8')).decode('utf-8')

    def _decrypt(self, key, msg):
        try:
            return self._decode(key.encode('utf-8'), msg.encode('utf-8')).decode('utf-8')
        except Exception as e:
            self.logger.error('wrong key given, can not decrypt.')
            exit(1)

    def _encode(self, key, clear):
        # https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = (clear[i] + key_c) % 256
            enc.append(enc_c)
        return base64.urlsafe_b64encode(bytes(enc))

    def _decode(self, key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = (enc[i] - key_c) % 256
            dec.append(dec_c)
        return bytes(dec)

    def _is_plugin(self):
        return not type(self).__name__ == 'Postcards'

    def _create_logger(self, logger=None):
        logging.addLevelName(LOGGING_TRACE_LVL, 'TRACE')
        logger = logger or logging.getLogger(inflection.underscore(type(self).__name__))
        setattr(logger, 'trace', lambda *args: logger.log(LOGGING_TRACE_LVL, *args))
        return logger

    def _configure_logging(self, logger, verbose_count=0):
        # set log level to INFO going more verbose for each new -v
        # most verbose is level trace which is 5
        logger.setLevel(int(max(2.0 - verbose_count, 0.5) * 10))

        api_wrapper_logger = logging.getLogger('postcard_creator')
        if logger.level <= logging.DEBUG:
            api_wrapper_logger.setLevel(logging.DEBUG)
        if logger.level <= LOGGING_TRACE_LVL:
            api_wrapper_logger.setLevel(5)

    def _build_root_parser(self, argv):
        parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                         description='Postcards is a CLI for the Swiss Postcard Creator')
        parser.epilog = 'browse https://github.com/abertschi/postcards for documentation, \n' \
                        'sourcecode and bug reports'

        parser.add_argument("-v", "--verbose", dest="verbose_count",
                            action="count", default=0,
                            help="increases log verbosity for each occurrence.")

        # parser.add_argument("-l", "--log-timestamp", dest="log_timestamp",
        #                     action="store_true",
        #                     help="output log messages with timestamp")
        self.enhance_root_subparser(parser)
        return parser

    def _build_subparser_decrypt(self, subparsers):
        parser_decrypt = subparsers.add_parser('decrypt', help='decrypt credentials')
        parser_decrypt.add_argument('credential', help='credential to decrypt', action='store')
        parser_decrypt.add_argument('-k', '--key', help='set a custom key to decrypt credential',
                                    default=self.default_key,
                                    action='store',
                                    dest='key')

        self.enhance_decrypt_subparser(parser_decrypt)

    def _build_subparser_encrypt(self, subparsers):
        parser_encrypt = subparsers.add_parser('encrypt', help='encrypt credentials to store in configuration file')

        parser_encrypt.add_argument('credential', help='credential to encrypt',
                                    action='store')

        parser_encrypt.add_argument('-k', '--key', help='set a custom key to encrypt credentials',
                                    action='store',
                                    default=self.default_key,
                                    dest='key')

        self.enhance_encrypt_subparser(parser_encrypt)

    def _build_subparser_generate(self, subparsers):
        parser_generate = subparsers.add_parser('generate', help='generate an empty configuration file',
                                                description='generate an empty configuration file')
        self.enhance_generate_subparser(parser_generate)

    def _build_subparser_send(self, subparsers):
        parser_send = subparsers.add_parser('send', help='send postcards',
                                            description='send postcards')
        parser_send.add_argument('-c', '--config',
                                 nargs=1,
                                 required=True,
                                 type=str,
                                 help='location to the configuration file (default: ./config.json)',
                                 default=[os.path.join(os.getcwd(), 'config.json')],
                                 dest='config_file')

        parser_send.add_argument('-a', '--accounts-file',
                                 default=False,
                                 help='location to a dedicated file containing postcard creator accounts',
                                 dest='accounts_file')

        parser_send.add_argument('-p', '--picture',
                                 required=not self._is_plugin(),
                                 help='postcard picture. path to an URL or image on disk',
                                 dest='picture')

        parser_send.add_argument('-m', '--message',
                                 default='',
                                 type=str,
                                 nargs=1,
                                 help='postcard message. you can use HTML tags to format the message (e.g. <br/>).',
                                 dest='message')

        parser_send.add_argument('--mock',
                                 action='store_true',
                                 help='do not submit postcard. useful for testing',
                                 dest='mock')

        parser_send.add_argument('--test-plugin',
                                 action='store_true',
                                 help='run plugin without configuration validation. useful for testing',
                                 dest='test_plugin')

        parser_send.add_argument('--username',
                                 default='',
                                 type=str,
                                 help='username credential. otherwise set in config or accounts file',
                                 dest='username')

        parser_send.add_argument('--password',
                                 default='',
                                 type=str,
                                 help='password credential. otherwise set in config or accounts file',
                                 dest='password')

        parser_send.add_argument('--all-accounts',
                                 action='store_true',
                                 help='run send command as often as valid accounts available',
                                 dest='all_accounts')

        parser_send.add_argument('-k', '--key',
                                 nargs='?',
                                 metavar="KEY",
                                 default=(None,),
                                 help='use this argument if your credentials are stored encrypted '
                                      + 'in configuration file. \n'
                                      + 'set your custom key if you are not using default key. \n'
                                      + '(i.e. --key PASSWORD instead of --key)',
                                 dest='key')
        self.enhance_send_subparser(parser_send)

    def _handle_message_argument(self, message):
        result = ''
        if isinstance(message, list):
            result = ' '.join(str(x) for x in message)
        elif isinstance(message, str):
            result = message
        return result

    def get_img_and_text(self, plugin_payload, cli_args):
        """
        To be overwritten by a plugin
        :param plugin_payload: plugin config from config file
        :param parser args added in Postcards.encrich_parser(). See docs of argparse
        :return: an image and text
        """
        return {'img': None, 'text': None}  # structure of object to return

    def build_plugin_subparser(self, subparsers):
        pass

    def enhance_root_subparser(self, parser):
        pass

    def enhance_generate_subparser(self, parser):
        pass

    def enhance_send_subparser(self, parser):
        pass

    def enhance_encrypt_subparser(self, parser):
        pass

    def enhance_decrypt_subparser(self, parser):
        pass

    def can_handle_command(self, command):
        return False

    def handle_command(self, command, args):
        pass


def main():
    p = Postcards()
    p.main(sys.argv)


if __name__ == '__main__':
    main()
