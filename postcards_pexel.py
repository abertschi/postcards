from postcards import Postcards
from util.pexels import get_random_image
import sys


class PexelPlugin(Postcards):
    def get_img_and_text(self, plugin_config, cli_args):
        return {
            'img': get_random_image(),
            'text': ''
        }

    def enrich_parser(self, parser):
        pass

if __name__ == '__main__':
    PexelPlugin().main(sys.argv[1:])
