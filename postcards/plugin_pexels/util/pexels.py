import random
import urllib
import base64
from pypexels import PyPexels

key = 'NTYzNDkyYWQ2ZjkxNzAwMDAxMDAwMDAxNmEzNTcyNDA4YmVjNGFmNzc0YTYzYTRjNjdjZGNkMGI='

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                  '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

pexels = PyPexels(api_key=base64.b64decode(key).decode('ascii'))


def get_random_image(keyword=None):
    if keyword is not None:
        print('Warn: keywords are no longer supported. image is chosen randomly.')

    url = get_random_image_url()
    return read_from_url(url)


def get_random_image_url(keyword=None):
    if keyword is not None:
        print('Warn: keywords are no longer supported. image is chosen randomly.')

    photos = pexels.curated(per_page=1, page=random.randint(1, 1000))
    entry = next(photos.entries)
    return entry.src['original']


def read_from_url(url):
    request = urllib.request.Request(url, None, headers)  # The assembled request
    return urllib.request.urlopen(request)


if __name__ == '__main__':
    imgs = get_random_image_url()
    print(imgs)
