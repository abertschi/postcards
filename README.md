# Postcards
> A CLI for the Swiss Postcard Creator

## Install
- Not yet available on pip

## Usage
```
sage: postcards.py [-h] [--config-file CONFIG_FILE]
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
## Plugins

### Send pictures from a folder

### Send pictures from http://pexels.com

## Related
- [postcard_creator_wrapper](https://github.com/abertschi/postcard_creator_wrapper) - Python API wrapper around the Swiss Postcard Creator

## Author
Andrin Bertschi

## License

MIT