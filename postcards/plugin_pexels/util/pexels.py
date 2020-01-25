import random
import requests
from bs4 import BeautifulSoup
import os
import urllib
import sys
import base64
from pypexels import PyPexels

#Decode pexels API key from abertschi
base64_message = 'NTYzNDkyYWQ2ZjkxNzAwMDAxMDAwMDAxNmEzNTcyNDA4YmVjNGFmNzc0YTYzYTRjNjdjZGNkMGIK'
base64_bytes = base64_message.encode('ascii')
message_bytes = base64.b64decode(base64_bytes)
api_key = message_bytes.decode('ascii')

# instantiate PyPexels object
py_pexel = PyPexels(api_key=api_key.rstrip())

words_location = os.path.dirname(os.path.realpath(__file__)) + '/words.txt'
pexels_search_url = 'http://api.pexels.com/v1/search?query='

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def get_random_image(keyword=None):
    url = get_random_image_url(keyword=keyword)
    return read_from_url(url)


def read_from_url(url):
    request = urllib.request.Request(url, None, headers)  # The assembled request
    return urllib.request.urlopen(request)


def get_random_image_url(keyword=None, number=1, _count=0):
    words = read_words()
    if keyword:
        search_term = keyword
    else:
        search_term = random.choice(words)
    search_results = py_pexel.search(query=search_term, per_page=40)
    imgs = []
    while True:
       for photo in search_results.entries:
           #print(photo.id, photo.photographer, photo.url)
           src = photo.src.get('original')
           imgs.append(src)
       if not search_results.has_next:
           break
       search_results = search_results.get_next_page()
    
    if imgs:
        chosen = []
        if number > len(imgs):
            number = len(imgs)

        for i in range(0, number):
            img = random.choice(imgs)
            imgs.remove(img)
            chosen.append(img)

        if number is 1:
            return chosen[0]
        else:
            return chosen
    elif _count < 10 and not keyword:
        return get_random_image_url(_count=_count + 1)
    elif keyword:
        raise Exception("No image found for keyword: " + keyword)
    else:
        raise Exception(f"Something is broken, tried {count} times but no images")


def read_words():
    with open(words_location) as f:
        content = f.readlines()
        return [x.strip() for x in content]


if __name__ == '__main__':
    keyword = None
    number = 1
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    if len(sys.argv) > 2:
        number = int(sys.argv[2])
    try:
        imgs = get_random_image_url(keyword=keyword, number=number)
        if isinstance(imgs, str):
            print(imgs)
        else:
            for url in imgs:
                print(url)
    except Exception as e:
        print(e)
        # raise e
