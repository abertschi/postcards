from postcards import Postcards
from util.pexels import get_random_image_url, read_from_url
import sys


class PostcardsPexel(Postcards):
    def get_img_and_text(self, plugin_config, cli_args):
        url = get_random_image_url()
        self.logger.info('using pexels picture: ' + url)
        return {
            'img': read_from_url(url),
            'text': ''
        }


if __name__ == '__main__':
    PostcardsPexel().main(sys.argv[1:])
