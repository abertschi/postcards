from postcard_creator import postcard_creator
import sys
import base64
import json
import os
import argparse

postcard_creator.Debug.debug = True


class Postcards:

    def main(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('--key', nargs=1, default=False)
        parser.add_argument('--encrypt', action="store", nargs=2, default=False)
        parser.add_argument('--decrypt', action="store", nargs=2, default=False)
        parser.add_argument('--config-file', default=os.path.dirname(os.path.realpath(__file__)) + '/config.json')
        parser.add_argument('--recipient-file', default=False)
        parser.add_argument('--sender-file', default=False)
        parser.add_argument('--accounts-file', default=False)
        parser.add_argument('--mock', action='store_true')
        parser.add_argument('--username', default=False)
        parser.add_argument('--password', default=False)
        parser.add_argument('--image', default=False)
        parser.add_argument('--message', default=False)
        parser.add_argument('--config-json', default=False)
        parser.add_argument('--payload-json', default=False)
        args = parser.parse_args()

        if args.encrypt:
            print(self._encrypt(args.encrypt[0], args.encrypt[1]))
            exit(0)

        config = self._read_config(args.config)
        accounts = []
        for account in config.get('accounts'):
            accounts.append({
                'username': account.get('username') if not args.key else self._decrypt(args.key,
                                                                                       account.get('username')),
                'password': account.get('password') if not args.key else self._decrypt(args.key,
                                                                                       account.get('password'))
            })

        if not accounts:
            print('No account given')
            exit(1)
        if not config.get('recipient'):
            print('No recipient sent in config file')
            exit(1)

        self.send(accounts=accounts,
                  recipient=config.get('recipient'),
                  sender=config.get('sender') if config.get('sender') else config.get('recipient'),
                  mock=str(args.mock), plugin_payload=config.get('payload'))

    def send(self, accounts, recipient, sender, mock=False, plugin_payload={}):
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

        img_and_text = self.get_img_and_text(plugin_payload)
        card = postcard_creator.Postcard(message=img_and_text['text'], recipient=self.create_recipient(recipient),
                                         sender=self.create_sender(sender),
                                         picture_stream=img_and_text['img'])

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

    def _read_config(self, location):
        with open(location) as f:
            return json.load(f)

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

    def _has_plugin(self):
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


if __name__ == '__main__':
    smc = Postcards()
    smc.main(sys.argv)
