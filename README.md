# Postcards

Postcards is a set of python scripts that allow you to send postcards with the Swiss Postcard Creator.

## Install
```
python setup.py install
```
Installation of `postcards` will expose these console scripts:
```
postcards
postcards-*
```
Issue `--help` for more information.

## Usage
```
$ postcards -h

usage: postcards [-h] [-v] {generate,send,encrypt,decrypt} ...

Postcards is a CLI for the Swiss Postcard Creator

positional arguments:
  {generate,send,encrypt,decrypt}
    generate            generate an empty configuration file
    send                send postcards
    encrypt             encrypt credentials to store in configuration file
    decrypt             decrypt credentials

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increases log verbosity for each occurrence.

sourcecode and documentation: https://github.com/abertschi/postcards

```

## Getting started
Create a configuration file by issuing 
```bash
$ postcards generate
```
A configuration file holds various information relevant to send postcards.
 
### Examples
Issue `postcards send --help` for more information about the available flags to set.

```bash
# Send a postcard
$ postcards send --config config.json \
    --picture https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg \
    --message "Happy coding"


# Encrypt user credentials to store in configuration file
$ postcards encrypt mypassword


# Send a postcard with encrypted credentials
$ postcards send --config config.json \
    --key \
    --picture https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg \
    --message "Happy coding"
```


## Plugins
Postcards is designed in a plugin based approach.

Note: Your picture (`--picture`) or the message text (`--message`) can always be overwritten by command line arguments if you use a plugin.

Example: 
```
postcards_folder send --config ./config.json --message "This overwrites the message set by the plugin"
```

### Plugin: postcards-folder
Send pictures from a folder.  

Add the following object to your configuration file
```json
{
 "payload": {
    "folder": "./pictures",
    "move": true
  }
}
```

- `folder`: location to a folder containing your images (required)
- `move`: set to false if sent picture should not be moved to a subdirectory `./sent/` (default: true)

#### Example
```
postcards-folder send --config ./my-config.json
```

### Plugin: postcards-pexels  
Send postcards with random pictures from www.pexels.com.

No configuration is necessary in your `config.json` file

#### Example
```
postcards-pexels send --config ./config.json
```

### Build your own plugin
See `postcards-pexels` for a sample.

1. Extend the class `postcards.Postcards()`
2. Overwrite `def get_img_and_text(self, payload, cli_args)`

## Related
- [postcard_creator_wrapper](https://github.com/abertschi/postcard_creator_wrapper) - Python API wrapper around the Swiss Postcard Creator

## Author
Andrin Bertschi and [friends](https://github.com/abertschi/postcards/graphs/contributors)

## License

MIT
