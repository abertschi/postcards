from postcard_creator import postcard_creator
import sys
import base64
import json
import os
import argparse, textwrap
from argparse import RawTextHelpFormatter
import urllib


class Postcards:
    def main(self, argv):
        args = self.get_argparser(argv)
        self.validate_cli_args(args=args)

        postcard_creator.Debug.debug = True  # always true?
        if args.trace:
            postcard_creator.Debug.debug = True
            postcard_creator.Debug.trace = True
        if args.debug:
            postcard_creator.Debug.debug = True

        if args.encrypt:
            print(self._encrypt(args.encrypt[0], args.encrypt[1]))
            exit(0)

        config = self._read_config(args.config[0])
        accounts = self._get_accounts_from_config(config)
        self._validate_config(config, accounts)

        self.send(accounts=accounts,
                  recipient=config.get('recipient'),
                  sender=config.get('sender') if config.get('sender') else config.get('recipient'),
                  mock=bool(args.mock),
                  plugin_payload=config.get('payload'),
                  picture_stream=self._read_picture(args.picture) if args.picture else None,
                  message=str(args.message),
                  cli_args=args)

    def send(self, accounts, recipient, sender, mock=False, plugin_payload={},
             message=None, picture_stream=None, cli_args=None):

        pcc_wrapper = None
        for account in accounts:
            token = postcard_creator.Token()
            if token.has_valid_credentials(account.get('username'), account.get('password')):
                pcc = postcard_creator.PostcardCreator(token)
                if pcc.has_free_postcard():
                    pcc_wrapper = pcc
                    break

        if not pcc_wrapper:
            print('error: No valid account given. Run later again or check accounts.')
            exit(1)

        if self._is_plugin():
            img_and_text = self.get_img_and_text(plugin_payload, cli_args=cli_args)
            message = img_and_text['text']
            picture_stream = img_and_text['img']  # TODO use tuples instead

        card = postcard_creator.Postcard(message=message,
                                         recipient=self._create_recipient(recipient),
                                         sender=self._create_sender(sender),
                                         picture_stream=picture_stream)


        # Never send postcard, because postcard_wrapper is not yet working correctly
        pcc_wrapper.send_free_card(card, mock_send=True)

        if not mock:
            print('Postcard sent!')
        else:
            print('Postcard not sent because of mock=True')

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

    def _get_accounts_from_config(self, config, key=None):
        accounts = []
        for account in config.get('accounts'):
            accounts.append({
                'username': account.get('username') if not key else self._decrypt(key, account.get('username')),
                'password': account.get('password') if not key else self._decrypt(key, account.get('password'))
            })
        return accounts

    def validate_cli_args(self, args):
        if not any([args.config, args.encrypt]):
            print('error: The following arguments are required: --config, or --encrypt')
            exit(1)

        if not self._is_plugin():
            if not args.picture and args.config:
                print('error: No picture set. Run a plugin or set --picture')
                exit(1)

    def _validate_config(self, config, accounts):
        if not accounts:
            print('error: No account set in config/accounts file')
            exit(1)

        if not config.get('recipient'):
            print('error: No recipient sent in config file')
            exit(1)

    def _read_config(self, location):
        location = self._make_absolute_path(location)
        if not os.path.isfile(location):
            print('error: Config file not found at ' + location)
            exit(1)

        with open(location) as f:
            return json.load(f)

    def _read_picture(self, location):
        if location.startswith('http'):
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}
            request = urllib.request.Request(location, None, headers)
            return urllib.request.urlopen(request)
        else:
            location = self._make_absolute_path(location)
            if not os.path.isfile(location):
                print('error: Picture not found at ' + location)
                exit(1)
            return open(location, 'rb')

    def _make_absolute_path(self, path):
        if os.path.isabs(path):
            return path
        else:
            return str(os.path.join(os.getcwd(), path))

    def _encrypt(self, key, msg):
        return self._encode(key, msg.encode('utf-8')).decode('utf-8')

    def _decrypt(self, key, msg):
        return self._decode(key, msg.encode('utf-8'))

    def _encode(self, key, clear):
        # https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = (ord(chr(clear[i])) + ord(key_c)) % 256
            enc.append(enc_c)
        return base64.urlsafe_b64encode(bytes(enc))

    def _decode(self, key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
            dec.append(dec_c)

    def _is_plugin(self):
        return not type(self).__name__ == 'Postcards'

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

    def get_argparser(self, argv):
        parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                         description='Postcards is a CLI for the Swiss Postcard Creator')
        parser.add_argument('--config', nargs=1, required=False, type=str,
                            help='location to the json config file')
        parser.add_argument('--accounts-file', default=False,
                            help='location to a dedicated json file containing postcard creator accounts')

        parser.add_argument('--picture', default=False,
                            help='postcard picture. path to an URL or image on disk')
        parser.add_argument('--message', default='',
                            help='postcard message')
        parser.add_argument('--key', nargs=1, default=False,
                            help='a key to decrypt credentials stored in config files: --key <password>')

        parser.add_argument('--username', default=False,
                            help='username credential. otherwise set in config or accounts file')
        parser.add_argument('--password', default=False,
                            help='password credential. otherwise set in config or accounts file')

        parser.add_argument('--encrypt', action="store", nargs=2, default=False,
                            help='encrypt credentials to store in config files: --encrypt <key> <credential>')

        parser.add_argument('--mock', action='store_true',
                            help='do not submit postcard. useful for testing')
        parser.add_argument('--trace', action='store_true',
                            help='enable tracing. useful for testing')
        parser.add_argument('--debug', action='store_true',
                            help='enable debug logs. useful for testing')

        parser.epilog = textwrap.dedent('''\
                sourcecode: https://github.com/abertschi/postcards
                    ''')
        self.enrich_parser(parser)
        return parser.parse_args()


if __name__ == '__main__':
    p = Postcards()
    p.main(sys.argv)
