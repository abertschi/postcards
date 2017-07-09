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

if sys.version_info < (3, 0):
    sys.stderr.write("Sorry, requires >= Python 3.x, not Python 2.x\n")
    sys.exit(1)

LOGGING_TRACE_LVL = 5
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(name)s (%(levelname)s): %(message)s')


class Postcards:
    def __init__(self, logger=None):
        self.logger = self._create_logger(logger)

    def main(self, argv):
        args = self.get_argparser(argv)
        self._configure_logging(self.logger, args.verbose_count)
        self.validate_cli_args(args=args)

        if args.encrypt:
            self.encrypt_credential(args.encrypt[0], args.encrypt[1])
            exit(0)
        elif args.decrypt:
            self.decrypt_credential(args.decrypt[0], args.decrypt[1])
            exit(0)

        config = self._read_config(args.config[0])
        accounts = self._get_accounts(config=config, key=args.key[0],
                                      username=args.username, password=args.password)
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

        self.logger.info('checking for valid accounts')
        pcc_wrapper = None
        for account in accounts:
            token = postcard_creator.Token()
            if token.has_valid_credentials(account.get('username'), account.get('password')):
                pcc = postcard_creator.PostcardCreator(token)
                if pcc.has_free_postcard():
                    pcc_wrapper = pcc
                    self.logger.info(f'account {account.get("username")} is valid')
                    break

        if not pcc_wrapper:
            self.logger.error('no valid account given. run later again or check accounts.')
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

    def validate_cli_args(self, args):
        if not any([args.config, args.encrypt, args.decrypt]):
            self.logger.error('the following arguments are required: --config, --encrypt, or --decrypt')
            exit(1)

        if not self._is_plugin():
            if not args.picture and not any([args.encrypt, args.decrypt]):
                self.logger.error('picture not set with --picture')
                exit(1)

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
            self.logger.fatal('config file not found at ' + location)
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
        return self._decode(key.encode('utf-8'), msg.encode('utf-8')).decode('utf-8')

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
        logger = logger or logging.getLogger(type(self).__name__.lower())
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

        parser.add_argument('--picture', default=False,
                            help='postcard picture. path to an URL or image on disk')
        parser.add_argument('--message', default='',
                            help='postcard message')
        parser.add_argument('--key', nargs=1, metavar="PASSWORD", default=(None,),
                            help='a key to decrypt credentials stored in config files')

        parser.add_argument('--username', default=None, type=str,
                            help='username credential. otherwise set in config or accounts file')
        parser.add_argument('--password', default=None, type=str,
                            help='password credential. otherwise set in config or accounts file')

        parser.add_argument('--encrypt', action="store", nargs=2, metavar=("KEY", "CREDENTIAL"), default=False,
                            help='encrypt credentials to store in config files')
        parser.add_argument('--decrypt', action="store", nargs=2, metavar=("KEY", "ENCRYPTED_TEXT"), default=False,
                            help='decrypt credentials')

        parser.add_argument('--mock', action='store_true',
                            help='do not submit postcard. useful for testing')

        parser.add_argument("-v", "--verbose", dest="verbose_count",
                            action="count", default=0,
                            help="increases log verbosity for each occurrence.")

        parser.epilog = 'sourcecode: https://github.com/abertschi/postcards'
        self.enrich_parser(parser)
        return parser.parse_args()


if __name__ == '__main__':
    p = Postcards()
    p.main(sys.argv)
