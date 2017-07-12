#!/usr/bin/env python
# encoding: utf-8

from postcards.postcards import Postcards
from postcards.plugin_pexels.util.pexels import get_random_image_url, read_from_url
import sys


class PostcardsPexel(Postcards):
    """
    Send postcards with random images from pexels.com
    """

    def get_img_and_text(self, plugin_config, cli_args):
        url = get_random_image_url()
        self.logger.info('using pexels picture: ' + url)
        return {
            'img': read_from_url(url),
            'text': ''
        }


def main():
    PostcardsPexel().main(sys.argv[1:])


if __name__ == '__main__':
    main()
