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

LOGGING_TRACE_LVL = 5
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(name)s (%(levelname)s): %(message)s')

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
        args = self.get_argparser(argv)
        self._configure_logging(self.logger, args.verbose_count)
        self._validate_cli_args(args=args)

        key_settings = self._parse_key(args)
        if args.encrypt:
            self.encrypt_credential(key_settings['key'], args.encrypt[0])
            exit(0)
        elif args.decrypt:
            self.decrypt_credential(key_settings['key'], args.decrypt[0])
            exit(0)
        elif args.generate:
            self._generate_config_file()
            exit(0)

        config = self._read_config(args.config[0])
        accounts = self._get_accounts(config=config, key=key_settings['key'] if key_settings['uses_key'] else None,
                                      username=args.username, password=args.password)
        random.shuffle(accounts)
        self._validate_config(config, accounts)

        self.send(accounts=accounts,
                  recipient=config.get('recipient'),
                  sender=config.get('sender') if config.get('sender') else config.get('recipient'),
                  mock=bool(args.mock),
                  plugin_payload=config.get('payload'),
                  picture_stream=self._read_picture(args.picture) if args.picture else None,
                  message=args.message,
                  cli_args=args)

    def send(self, accounts, recipient, sender, mock=False, plugin_payload={},
             message=None, picture_stream=None, cli_args=None):

        if cli_args and cli_args.test_plugin:
            self.logger.info('running plugin only (--test-plugin)')
            self.get_img_and_text(plugin_payload, cli_args=cli_args)
            exit(0)

        self.logger.info('checking for valid accounts')
        pcc_wrapper = None
        try_again_after = ''
        for account in accounts:
            token = postcard_creator.Token()
            if token.has_valid_credentials(account.get('username'), account.get('password')):
                pcc = postcard_creator.PostcardCreator(token)
                if pcc.has_free_postcard():
                    pcc_wrapper = pcc
                    self.logger.info(f'account {account.get("username")} is valid')
                    break
                else:
                    next_quota = pcc.get_quota().get('next')
                    if next_quota < try_again_after or try_again_after is '':
                        try_again_after = next_quota

                    self.logger.debug(f'account {account.get("username")} is invalid. ' +
                                      f'new quota available after {next_quota}.')
            else:
                self.logger.warning(f'wrong user credentials for {account.get("username")}')

        if not pcc_wrapper:
            self.logger.error(f'no valid account given. try again after {try_again_after}')
            exit(1)

        if self._is_plugin():
            img_and_text = self.get_img_and_text(plugin_payload, cli_args=cli_args)

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
            pcc_wrapper.send_free_card(card, mock_send=mock)
        except Exception as e:
            self.logger.fatal('can not send postcard: ' + str(e))
            raise e

        if mock:
            self.logger.info('postcard not sent because of mock=True')
        else:
            self.logger.info('postcard is successfully sent')

    def encrypt_credential(self, key, credential):
        self.logger.info('encrypted credential:')
        self.logger.info(self._encrypt(key, credential))

    def decrypt_credential(self, key, credential):
        self.logger.info('decrypted credential:')
        self.logger.info(self._decrypt(key, credential))

    def _generate_config_file(self):
        target_location = str(os.path.join(os.getcwd(), 'config.json'))
        if os.path.isfile(target_location):
            self.logger.error('config file already exist in current directory.')
            exit(1)

        content = pkg_resources.resource_string(__name__, 'static/template_config.json').decode('utf-8')
        file = open(target_location, 'w')
        file.write(content)
        file.close()
        self.logger.info('empty config file generated at {}'.format(target_location))

    def _create_recipient(self, recipient):
        return postcard_creator.Recipient(prename=recipient.get('firstname'),
                                          lastname=recipient.get('lastname'),
                                          street=recipient.get('street'),
                                          zip_code=recipient.get('zipcode'),
                                          place=recipient.get('city'))

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

    def _validate_cli_args(self, args):
        if not any([args.config, args.encrypt, args.decrypt, args.generate]):
            self.logger.error('the following arguments are required: --config, --encrypt, --decrypt, --generate')
            exit(1)

        if not self._is_plugin():
            if not args.picture and not any([args.encrypt, args.decrypt, args.generate]):
                self.logger.error('picture not set with --picture')
                exit(1)

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

    def _read_config(self, location):
        location = self._make_absolute_path(location)
        self.logger.info('reading config file ' + location)

        if not os.path.isfile(location):
            self.logger.fatal('config file not found at ' + location + ' . set config file with --config flag')
            exit(1)
        try:
            with open(location) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error('can not parse config file ' + location + '. is it valid json ?')
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

    def _create_logger(self, logger):
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

    def get_img_and_text(self, plugin_payload, cli_args):
        """
        To be overwritten by a plugin
        :param plugin_payload: plugin config from config file
        :param parser args added in Postcards.encrich_parser(). See docs of argparse
        :return: an image and text
        """
        raise Exception('Dont run this class directly. Use a plugin instead')
        return {'img': None, 'text': None}  # structure of object to return

    def enrich_parser(self, parser):
        """
        A plugin can add CLI options to the parser
        :param parser:
        :return: nothing
        """
        pass

    def get_logger(self):
        return self.logger

    def get_argparser(self, argv):
        parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                         description='Postcards is a CLI for the Swiss Postcard Creator')
        parser.add_argument('--config', nargs=1, required=False, type=str,
                            help='location to the json config file (default: ./config.json)', default=['config.json'])
        # parser.add_argument('--accounts-file', default=False,
        #                     help='location to a dedicated json file containing postcard creator accounts')

        parser.add_argument('--generate', required=False, action='store_true',
                            help='generate an empty config file')

        parser.add_argument('--picture', default=False,
                            help='postcard picture. path to an URL or image on disk')
        parser.add_argument('--message', default='',
                            help='postcard message')

        parser.add_argument('--username', default=None, type=str,
                            help='username credential. otherwise set in config or accounts file')
        parser.add_argument('--password', default=None, type=str,
                            help='password credential. otherwise set in config or accounts file')

        parser.add_argument('--key', nargs='?', metavar="KEY", default=(None,),
                            help='use this argument if your credentials are stored encrypted in config file. \n'
                                 + 'set your custom key if you are not using default key. \n'
                                 + '(i.e. --key PASSWORD instead of --key)')
        parser.add_argument('--encrypt', action="store", nargs=1, metavar="CREDENTIAL", default=False,
                            help='encrypt credentials with default key. \n' +
                                 'use --key argument to use custom key.')
        parser.add_argument('--decrypt', action="store", nargs=1, metavar="ENCRYPTED_TEXT", default=False,
                            help='decrypt credentials with default key. use --key argument to use custom key.')

        parser.add_argument('--mock', action='store_true',
                            help='do not submit postcard. useful for testing')

        parser.add_argument('--test-plugin', action='store_true',
                            help='run plugin without config validation. useful for testing')

        parser.add_argument("-v", "--verbose", dest="verbose_count",
                            action="count", default=0,
                            help="increases log verbosity for each occurrence.")

        parser.epilog = 'sourcecode: https://github.com/abertschi/postcards'
        self.enrich_parser(parser)
        return parser.parse_args()


def main():
    p = Postcards()
    p.main(sys.argv)


if __name__ == '__main__':
    main()
