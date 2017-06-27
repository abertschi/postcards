from postcards import Postcards
from util.pexels import get_random_image_url, read_from_url
import sys


class PexelsPlugin(Postcards):
    def get_img_and_text(self, plugin_config, cli_args):
        url = get_random_image_url()
        print('Using pexels picture: ' + url)
        return {
            'img': read_from_url(url),
            'text': ''
        }


if __name__ == '__main__':
    PexelsPlugin().main(sys.argv[1:])
