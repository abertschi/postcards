from postcards.postcards import Postcards
from postcards.plugin_pexels.util.pexels import get_random_image_url, read_from_url
import sys
import json
import os
import random
import nltk

jokes_location = os.path.dirname(os.path.realpath(__file__)) + '/chuck_norris_jokes.json'
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


class PostcardsChuckNorris(Postcards):
    """
    Send a postcard with a chuck norris joke.
    Parse the joke for nouns and choose a matching picture on pexels.com

    """

    def enhance_send_subparser(self, parser):
        parser.add_argument('--category', default=None, type=str,
                            help='choose a custom joke category: nerdy, explicit')
        parser.add_argument('--duplicate-file', default=None, type=str,
                            help='avoid sending the same joke twice by setting a file which stores already sent jokes')

    def get_img_and_text(self, plugin_payload, cli_args):
        jokes = self._read_jokes()

        if cli_args.category:
            jokes = self._filter_by_category(jokes, cli_args.category)

        if not jokes:
            self.logger.error('No jokes found for category: {}'.format(cli_args.category))
            exit(1)

        exclude_jokes = []

        if cli_args.duplicate_file:
            exclude_file = self._make_absolute_path(cli_args.duplicate_file)
            if os.path.isfile(exclude_file):
                with open(exclude_file) as f:
                    content = f.readlines()
                    exclude_jokes = [x.strip() for x in content]

        jokes = self._filter_by_exclude_id(jokes, exclude_jokes)

        if not jokes:
            self.logger.error('No more jokes to choose from. everything excluded by {}'.format(cli_args.duplicate_file))
            exit(1)

        joke = random.choice(jokes)
        postcard_text = joke.get('joke')
        nouns = self._find_nouns(postcard_text)

        keyword = ''
        counter = 0
        for n in nouns:
            if counter > 2:
                break
            keyword += n + ' '
            counter = counter + 1
            self.logger.debug(n)

        keyword = keyword.strip()
        if keyword:
            try:
                url = get_random_image_url(keyword=keyword)
            except Exception:
                url = get_random_image_url()
        else:
            url = get_random_image_url()

        self.logger.debug('keyword: {}, text: {}'.format(keyword, postcard_text))
        self.logger.debug('url: {}'.format(url))

        if cli_args.duplicate_file:
            with open(exclude_file, "a") as excludes:
                excludes.write(str(joke.get('id')) + '\n')

        return {
            'img': read_from_url(url),
            'text': postcard_text
        }

    def _read_jokes(self):
        with open(jokes_location, 'r') as f:
            jokes = json.loads(f.read())
            return jokes.get('value')

    def _find_nouns(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        nouns = [word for word, pos in tagged \
                 if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]

        filter_keywords = ['chuck', 'norris', 'quot']
        filtered = [i for i in nouns if not any(f in i.lower() for f in filter_keywords)]
        return filtered

    def _make_absolute_path(self, path):
        if os.path.isabs(path):
            return path
        else:
            return str(os.path.join(os.getcwd(), path))

    @staticmethod
    def _filter_by_category(jokes, category):
        result = []
        for val in jokes:
            if category in val.get('categories'): result.append(val)
        return result

    @staticmethod
    def _filter_by_exclude_id(jokes, exclude_id_list):
        result = []
        for val in jokes:
            if val.get('id') not in exclude_id_list: result.append(val)
        return result


def main():
    PostcardsChuckNorris().main(sys.argv[1:])


if __name__ == '__main__':
    main()
