# Postcards
> A CLI for the Swiss Postcard Creator

## Install
- Not yet available on pip

## Usage
```
python postcards.py --help 
usage: postcards.py [-h] [--config-file CONFIG_FILE]
                    [--recipient-file RECIPIENT_FILE]
                    [--sender-file SENDER_FILE]
                    [--accounts-file ACCOUNTS_FILE] [--image IMAGE]
                    [--message MESSAGE] [--key KEY] [--username USERNAME]
                    [--password PASSWORD] [--encrypt ENCRYPT ENCRYPT]
                    [--decrypt DECRYPT DECRYPT] [--mock] [--trace]

Postcards is a CLI for the Swiss Postcard Creator

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        location to the json config file
  --recipient-file RECIPIENT_FILE
                        location to a dedicated json file containing the recipient
  --sender-file SENDER_FILE
                        location to a dedicated json file containing the sender
  --accounts-file ACCOUNTS_FILE
                        location to a dedicated json file containing postcard creator accounts
  --image IMAGE         postcard picture. path to an URL or image on disk
  --message MESSAGE     postcard message
  --key KEY             a key to decrypt credentials stored in config files: --key <password>
  --username USERNAME   username credential. otherwise set in config or accounts file
  --password PASSWORD   password credential. otherwise set in config or accounts file
  --encrypt ENCRYPT ENCRYPT
                        encrypt credentials to store in config files: --encrypt <key> <credential>
  --decrypt DECRYPT DECRYPT
                        decrypt credentials: --decrypt <key> <credential>
  --mock                do not submit postcard. useful for testing
  --trace               enable tracing. useful for testing

example use:

use a config file:
        postcards.py --config-file config.json 
                     --key <key_to_decrypt_credentials> \
                     --message 'My postcard' --picture ./picture.jpg

pass credentials as arguments and use dedicated config files:
        postcards.py --sender-file sender.json \
          --recipient-file recipient.json \
          --username <username> \
          --password <password> \
          --message message \
          --picture ./picture.jpg

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

```
## Plugins

### Send pictures from a folder

### Send pictures from http://pexels.com

## Related
- [postcard_creator_wrapper](https://github.com/abertschi/postcard_creator_wrapper) - Python API wrapper around the Swiss Postcard Creator

## Author
Andrin Bertschi

## License

MIT