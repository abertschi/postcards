from postcards import Postcards
import sys
import random
import requests
from bs4 import BeautifulSoup
import os
import urllib
import sys
import re, util


search_url = 'http://www.diddly.com/random/'


class PostcardsBingRandom(Postcards):
    def get_img_and_text(self, plugin_config, cli_args):

        soup = util.mysoupopen(search_url)

        images = []
        for img in soup.findAll("img", {"class": "mimg"}):
            print(img)
            src = img['src']
            images.append(src)

        for i in images:
            print(i)

        return {
            'img': None,
            'text': ''
        }


if __name__ == '__main__':
    PostcardsBingRandom().get_img_and_text(None, None)
