from postcard_creator import postcard_creator
import sys
import base64
import json
import os
import argparse, textwrap
from argparse import RawTextHelpFormatter

postcard_creator.Debug.debug = True


class Postcards:
    def main(self, argv):
        args = self.get_argparser(argv)
        if args.encrypt:
            print(self._encrypt(args.encrypt[0], args.encrypt[1]))
            exit(0)

        config = self._read_config(args.config)
        accounts = self._get_accounts_from_config(config)

        if not accounts:
            print('No account given')
            exit(1)

        if not config.get('recipient'):
            print('No recipient sent in config file')
            exit(1)

        if not self._is_plugin():
            message = args.message
            picture = args.picture
            if not picture:
                print('No --picture set. Run a plugin or set --picture')
                exit(1)
            picture = self._read_picture(picture)

        self.send(accounts=accounts,
                  recipient=config.get('recipient'),
                  sender=config.get('sender') if config.get('sender') else config.get('recipient'),
                  mock=bool(args.mock),
                  plugin_payload=config.get('payload'),
                  picture_stream=picture,
                  message=str(message))

    def send(self, accounts, recipient, sender, mock=False, plugin_payload={}, message=None, picture_stream=None):
        pcc_wrapper = None
        for account in accounts:
            token = postcard_creator.Token()
            if token.has_valid_credentials(account.get('username'), account.get('password')):
                pcc = postcard_creator.PostcardCreator(token)
                if pcc.has_free_postcard():
                    pcc_wrapper = pcc
                    break

        if not pcc_wrapper:
            print('No valid account given. Run later again or check accounts')
            exit(1)

        if self._is_plugin():
            img_and_text = self.get_img_and_text(plugin_payload)
            message = img_and_text['text']
            picture_stream = img_and_text['img']

        card = postcard_creator.Postcard(message=message, recipient=self.create_recipient(recipient),
                                         sender=self.create_sender(sender),
                                         picture_stream=picture_stream)
        pcc_wrapper.send_free_card(card, mock_send=mock)

    def create_recipient(self, recipient):
        return postcard_creator.Recipient(prename=recipient.get('firstname'),
                                          lastname=recipient.get('lastname'),
                                          street=recipient.get('street'),
                                          zip_code=recipient.get('zipcode'),
                                          place=recipient.get('city'))

    def create_sender(self, sender):
        return postcard_creator.Sender(prename=sender.get('firstname'),
                                       lastname=sender.get('lastname'),
                                       street=sender.get('street'),
                                       zip_code=sender.get('zipcode'),
                                       place=sender.get('city'))

    def _get_accounts_from_config(self, config, key=None):
        accounts = []
        for account in config.get('accounts'):
            accounts.append({
                'username': account.get('username') if not key
                else self._decrypt(key, account.get('username')),
                'password': account.get('password') if not key
                else self._decrypt(key, account.get('password'))
            })
        return accounts

    def _read_config(self, location):
        with open(location) as f:
            return json.load(f)

    def _read_picture(self, location):
        return ''

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
        try:
            self.get_img_and_text(None)
            return True
        except Exception:
            return False

    def get_img_and_text(self, plugin_payload):
        """
        To be overwritten by a plugin
        :param plugin_payload: plugin config from config file
        :return: an image and text
        """
        raise Exception('Dont run this class directly. Use a plugin instead')
        return {'img': None, 'text': None}

    def get_argparser(self, argv):
        parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                         description='Postcards is a CLI for the Swiss Postcard Creator')
        parser.add_argument('--config-file', default=os.path.dirname(os.path.realpath(__file__)) + '/config.json',
                            help='location to the json config file')
        parser.add_argument('--recipient-file', default=False,
                            help='location to a dedicated json file containing the recipient')
        parser.add_argument('--sender-file', default=False,
                            help='location to a dedicated json file containing the sender')
        parser.add_argument('--accounts-file', default=False,
                            help='location to a dedicated json file containing postcard creator accounts')

        parser.add_argument('--image', default=False,
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
        parser.add_argument('--decrypt', action="store", nargs=2, default=False,
                            help='decrypt credentials: --decrypt <key> <credential>')

        parser.add_argument('--mock', action='store_true',
                            help='do not submit postcard. useful for testing')
        parser.add_argument('--trace', action='store_true',
                            help='enable tracing. useful for testing')

        parser.epilog = textwrap.dedent('''\

                example use:

                use a config file:
                \tpostcards.py --config-file config.json 
                \t             --key <key_to_decrypt_credentials> \\
                \t             --message 'My postcard' --picture ./picture.jpg

                pass credentials as arguments and use dedicated config files:
                \tpostcards.py --sender-file sender.json \\
                \t  --recipient-file recipient.json \\
                \t  --username <username> \\
                \t  --password <password> \\
                \t  --message message \\
                \t  --picture ./picture.jpg


                sample config file:

                {
                  "recipient": {
                    "firstname": "",
                    "lastname": "",
                    "street": "",
                    "zipcode": "",
                    "city": ""
                  },
                  "sender": {
                    "firstname": "",
                    "lastname": "",
                    "street": "",
                    "zipcode": "",
                    "city": ""
                  },
                  "accounts": [
                    {
                      "username": "",
                      "password": ""
                    }
                  ]
                }


                github: https://github.com/abertschi/postcards
                Andrin Bertschi 2017, MIT

                ''')
        return parser.parse_args()


if __name__ == '__main__':
    smc = Postcards()
    smc.main(sys.argv)
