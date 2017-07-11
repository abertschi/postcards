from setuptools import setup, find_packages
from pip.req import parse_requirements
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))
install_reqs = parse_requirements('./requirements.txt', session='hack')
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
    version=find_version('postcards', '__init__.py'),
    url='http://github.com/abertschi/postcards',
    author='Andrin Bertschi',
    install_requires=reqs,
    description='',
    packages=find_packages(exclude=("tmp",)),
    platforms='any',
    keywords='postcard swiss',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.6',
    ],
    package_data={'postcards': ['template_config.json']},
    extras_require={

    },
    entry_points={
        'console_scripts': ['postcards=postcards.postcards:main',
                            'postcards-folder=postcards.plugin_folder.postcards_folder:main',
                            'postcards-pexels=postcards.plugin_pexels.postcards_pexels:main',
                            'postcards-random=postcards.plugin_random.postcards_random:main'],
    }
)
