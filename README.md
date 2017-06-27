# Postcards
> A CLI for the Swiss Postcard Creator

## Install
- Not yet available on pip

## Usage
```
python postcards.py --help

Usage: postcards.py [-h] [--config-file CONFIG_FILE]
                    [--accounts-file ACCOUNTS_FILE] [--image IMAGE]
                    [--message MESSAGE] [--key KEY] [--username USERNAME]
                    [--password PASSWORD] [--encrypt ENCRYPT ENCRYPT]
                    [--decrypt DECRYPT DECRYPT] [--mock] [--trace]

Postcards is a CLI for the Swiss Postcard Creator

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        location to the json config file
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

```

## configuration file
```json
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

```

## Plugins

### Send pictures from a folder
Plugin name: `postcards_folder.py`  
This plugin sends pictures from a folder

Add the following object to your configuration file (config.json)
```json
{
 "payload": {
    "folder": "./pictures",
    "move": true
  }
}
```

- folder: location to a folder containing your images (required)
- move: set to false if sent picture should not be moved to a subdirectory `./sent/` (default: true)

### Send pictures from http://pexels.com
- Plugin name: `postcards_pexels.py`  
This plugin chooses random pictures from pexels.

### Build your own plugin
See `postcards_pexels.py` or `postcards_folder.py` for a sample

1. Extend the class `postcards.Postcards()`
2. Overwrite `def get_img_and_text(self, payload, cli_args)`
3. Optionally add command line args by overwriting `def enrich_parser(self, parser)`

## Related
- [postcard_creator_wrapper](https://github.com/abertschi/postcard_creator_wrapper) - Python API wrapper around the Swiss Postcard Creator

## Author
Andrin Bertschi

## License

MIT