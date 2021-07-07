# Postcards [![PyPI version](https://img.shields.io/pypi/v/postcards.svg)](https://badge.fury.io/py/postcards)

Postcards is a set of python scripts that allow you to send postcards with the Swiss Postcard Creator.

## Install
This package requires python 3.6 or later.

```sh
# pip for python3 is required
pip install postcards
```

or install from source

```sh
git clone git@github.com:abertschi/postcards.git
cd postcards/
pip install .
```

Installation of `postcards` will expose these console scripts:
```
postcards
postcards-folder
postcards-yaml
postcards-pexels
postcards-random
postcards-chuck-norris
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
A [configuration file](./postcards/template_config.json) 
holds various information relevant to send postcards.
 
### Examples
Issue `postcards send --help` for more information about sending postcards.

```bash
# Send a postcard
$ postcards send --config config.json \
    --picture https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg \
    --message "Happy <br/> coding!"


# Encrypt user passwords to store in configuration file
$ postcards encrypt mypassword


# Send a postcard with encrypted passwords stored in configuration file
$ postcards send --config config.json \
    --key \
    --picture https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg \
    --message "Happy coding"
    
# Increase verbosity
$ postcards -v send --config config.json \
    --picture https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg \
    --message "Happy <br/> coding!"

# - Add more 'v' to increase verbosity, i.e. -vv
# - Note: The -v / --verbose flag belongs to the root parser, add it after 'postcards' and before 'send'     
    
```

## Plugins
Postcards is designed in a plugin based approach. 
Plugins set the text and / or picture of your postcards.

Postcard pictures and text can always be overwritten by commandline by issuing 
`--picture <picutre>` and `--message <message>`.

These plugins are available:
- [Plugin: postcards-folder](#plugin-postcards-folder)
- [Plugin: postcards-yaml](#plugin-postcards-yaml)
- [Plugin: postcards-pexels](#plugin-postcards-pexels)
- [Plugin: postcards-random](#plugin-postcards-random)
- [Plugin: postcards-chuck-norris](#plugin-postcards-chuck-norris)
- [Build your own plugin](#build-your-own-plugin)

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
$ postcards-folder send --config ./my-config.json --message "coding rocks"
```
#### Slice a picture into tiles
`postcards-folder` comes with a command called `slice` to create tiles from an image.
This is useful to create a poster-like picture with postcards.

Issue `postcards-folder slice --help` for more information.

### Plugin: postcards-yaml
Specify what picture and text to send in a YAML file. This allows for scripted bulk sending
and extends `postcards-folder` with a YAML file.


Add the following object to your configuration file (`config.json`);
```json
{
 "payload": {
    "folder": "./pictures",
    "yaml": "./pictures/send.yaml",
    "move": true
  }
}
```

Create a YAML file in the following format;

```yaml
- This is the text for postcard 1
- this-location-to-picture-1.jpg
- This is the text for postcard 2
- this-is-location-to-picture-2.jpg
```

- Entry `i` contains text, and entry `i+1` contains the relative location of the picture.
- For all `i modulo 2 == 0`, `i >= 0`
- The absolute location of the image consists of the `folder` path in `config.json` and the image location in the YAML file.
- Entries are removed from the YAML file if a postcard is sent.
- Entries are picked as they appear in the YAML file.

#### Example
```
$ postcards-yaml send --config ./config.json
```
- see directory `./example/plugin_yaml/` for more examples.

#### Validate YAML file
You can verify the YAML file with `postcards-yaml validate -c config.json`.
This command checks that all pictures exist and the YAML file has
proper format.

### Plugin: postcards-pexels  
Send postcards with random pictures from www.pexels.com.

No configuration is necessary in your configuration file.

#### Example
```
$ postcards-pexels send --config ./config.json --message "coding rocks"
```

### Plugin: postcards-random
Surprise, surprise! This plugin chooses an arbitrary picture from the 
internet as postcard picture.
Picture may be inappropriate, so use with caution.

No configuration is necessary in your configuration file.
Needs python 3.6, newer versions cause some errors (TODO).

#### Example
```
$ postcards-random send --config ./config.json \
  --message "So much of life, it seems to me, is determined by pure randomness. \
   So is this postcard picture."
```

### Plugin: postcards-chuck-norris  
Chuck Norris's first program was kill -9!

Receive postcards with Chuck Norris statements.
No configuration is necessary in your configuration file.

#### Example
```
$ postcards-chuck-norris send --config ./config.json --category nerdy --duplicate-file duplicates.txt
```
- Issue `postcards-chuck-norris send --help` for more information about the additional flags.

### Build your own plugin
1. Extend the class `postcards.Postcards()`
2. Overwrite `def get_img_and_text(self, payload, cli_args)`
3. Add CLI parser functionality by overwriting `enhance_*_subparser` methods

```python
from postcards.postcards import Postcards
import sys

class MyPlugin(Postcards):

    def get_img_and_text(self, plugin_config, cli_args):
      return {
            'img': '...',
            'text': '...'
        }
        
if __name__ == '__main__':
    MyPlugin().main(sys.argv[1:])
        
```
```sh
$ python my_plugin.py --help
```
## FAQ
### Something does not work, can you help?
- 1 Update to latest version
- 2 Check current issues for workaround steps
  - https://github.com/abertschi/postcard_creator_wrapper/issues
  - https://github.com/abertschi/postcards/issues
- 3 File a new issue 

## Release notes
### v2.2, 2021-07-07
- update to postcard-creator-wrapper to v2.2

### v2.1, 2021-05-16
- update postcard-creator-wrapper to v2.1

### v2.0, 2021-02 #49
- `plugin_folder`: introduce `.priority` folder to prioritize images #40
- mics: removed dependency on internal pip api #38
- use postcard_creator 2.0 to fix issues with swissid authentication method #46
- fix message parsing issue #41

### v1.1, 2020-01-30
- update to postcard-creator 1.1. swissid authentication is now supported

### v1.0, 2020-01-28
- `plugin_random`: needs python 3.6 to work, newer versions are currently not supported
- `plugin_pexel`: use official pexel API, keyword is no longer supported
- `plugin_yaml`: introduction of new plugin
  - `postcards-yaml` reads a YAML file with text/picture entries. This allows for scripted bulk sending.
  - see `postcards-yaml -h` or documentation above for more information

### v0.0.8, 2018-03-28
- v0.0.7 broke due to changes in the postcardcreator API
 - update `postcard-creator` to `0.0.8`

### v0.0.7, 2017-11-22
- Bug fixing release
- Remove unused dependencies
- update `postcard-creator` API wrapper to `0.0.6`

### v0.0.6, 2017-08-13
- Bug fixing

### v0.0.5, 2017-08-12
- Introduce new plugin `postcards-chuck-norris`
- Add flag `--all-accounts` to global `postcards`


## Development notes
```sh
pip install -r requirements-dev.txt
pip install -e .
```

## Related
- [postcard_creator_wrapper](https://github.com/abertschi/postcard_creator_wrapper) - Python API wrapper around the Swiss Postcard Creator

## Author
Andrin Bertschi and [friends](https://github.com/abertschi/postcards/graphs/contributors)

## License

MIT
