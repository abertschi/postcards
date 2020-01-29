try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

from setuptools import setup, find_packages

import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))
install_reqs = parse_requirements(here + '/requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='postcards',
    version='1.0',
    url='http://github.com/abertschi/postcards',
    author='Andrin Bertschi',
    description='A CLI for the Swiss Postcard Creator',
    packages=find_packages(exclude=("tmp",)),
    platforms='any',
    keywords='postcard swiss',
    classifiers=[
    ],
    package_data={'postcards': ['template_config.json',
                                'plugin_chuck_norris/chuck_norris_jokes.json']},
    setup_requires=[
    ],

    install_requires=reqs,
    entry_points={
        'console_scripts': ['postcards=postcards.postcards:main',
                            'postcards-folder=postcards.plugin_folder.postcards_folder:main',
                            'postcards-yaml=postcards.plugin_folder_yaml.postcards_folder_yaml:main',
                            'postcards-pexels=postcards.plugin_pexels.postcards_pexels:main',
                            'postcards-random=postcards.plugin_random.postcards_random:main',
                            'postcards-chuck-norris=postcards.plugin_chuck_norris.postcards_chuck_norris:main'],
    }
)
