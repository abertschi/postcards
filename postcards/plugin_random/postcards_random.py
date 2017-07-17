#!/usr/bin/env python
# encoding: utf-8

from postcards.postcards import Postcards
import urllib
from postcards.plugin_random.random_search_term.random_search_term import get_random_search_term
from bs4 import BeautifulSoup
import json
import urllib.request, urllib.error, urllib.parse
import random
import sys

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


class PostcardsRandom(Postcards):
    """
    Get an arbitrary picture from the internet as postcard image.
    Note: image may be inappropriate

    Use flag --keyword <keyword> to search for specific images
    Use flag --safe-search to enable safe search
    """

    def enhance_send_subparser(self, parser):
        parser.add_argument('--keyword', default=None, type=str,
                            help='use custom keyword to search for images')
        parser.add_argument('--safe-search', default=False, action='store_true',
                            help='enable safe search')

    def get_img_and_text(self, plugin_config, cli_args):
        imgs = []
        enable_safe_search = True if cli_args.safe_search else False
        self.logger.debug('setting image safe search to {}'.format(enable_safe_search))

        if cli_args.keyword:
            self.logger.info('using custom keyword {}'.format(cli_args.keyword))
            imgs = self._fetch_img_urls(cli_args.keyword, safe_search=enable_safe_search)
        else:
            imgs = self._get_images_for_random_keyword(safe_search=enable_safe_search)

        if not imgs:
            self.logger.error('no images found for given keyword')
            exit(1)

        if cli_args.keyword:
            img = random.choice(imgs)[2]
        else:
            img = imgs[0][2]  # always choose first img because search key is random anyway

        self.logger.info('choosing image {}'.format(img))
        return {
            'img': self._read_from_url(img),
            'text': ''
        }

    def _get_images_for_random_keyword(self, safe_search=False):
        found = False
        counter = 0

        imgs = []
        while not found and counter < 10:
            keyword = self._get_search_term()
            self.logger.debug('trying to search for images with keyword=' + keyword)

            imgs = self._fetch_img_urls(keyword, safe_search=safe_search)
            self.logger.trace(imgs)
            self.logger.debug('fetched {} images'.format(len(imgs)))

            counter += 1
            if len(imgs) > 0:
                found = True
        return imgs

    def _get_search_term(self):
        try:
            return get_random_search_term()
        except Exception as e:
            self.logger.error('something broke with the generated python code')
            raise e

    def _get_bing_url(self, keyword, safe_search=False, large_size=True):
        if large_size:
            keyword += '+filterui:imagesize-large'

        url = "http://www.bing.com/images/search?q=" + keyword + "&FORM=HDRSC2"

        if not safe_search:
            url += '&adlt=off'

        return url

    def _fetch_img_urls(self, keyword, safe_search=False):
        # bing img search, https://gist.github.com/stephenhouser/c5e2b921c3770ed47eb3b75efbc94799

        url = self._get_bing_url(keyword, safe_search=safe_search)
        self.logger.debug('search url {}'.format(url))

        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/43.0.2357.134 Safari/537.36"}

        soup = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url, headers=header)), 'html.parser')
        imgs = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("a", {"class": "iusc"}):
            mad = json.loads(a["mad"])
            turl = mad["turl"]
            m = json.loads(a["m"])
            murl = m["murl"]

            image_name = urllib.parse.urlsplit(murl).path.split("/")[-1]
            imgs.append((image_name, turl, murl))

        return imgs

    def _read_from_url(self, url):
        request = urllib.request.Request(url, None, headers)
        return urllib.request.urlopen(request)


def main():
    PostcardsRandom().main(sys.argv[1:])


if __name__ == '__main__':
    main()
