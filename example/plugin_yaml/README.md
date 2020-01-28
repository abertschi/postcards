## Examples for postcards-yaml

- assume that package is installed and available

```sh
# info
postcards-yaml -h

# verify that YAML file is correct and all referenced images exist
postcards-yaml validate -c myconfig.json

# send a card
postcards-yaml send -c myconfig.json

# dry run, do not send
postcards-yaml send -c myconfig.json --mock

# test plugin without postcard-creator API
postcards-yaml send -c myconfig.json --test-plugin
```
