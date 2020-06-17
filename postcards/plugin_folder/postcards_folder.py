#!/usr/bin/env python
# encoding: utf-8

from postcards.postcards import Postcards
from postcards.plugin_folder.slice_image import make_tiles, store_tiles
import sys
import os
import random
import ntpath
from PIL import Image
import os
from time import gmtime, strftime


class PostcardsFolder(Postcards):
    """
    Send postcards with images from a local folder
    """

    supported_ext = ['.jpg', '.jpeg', '.png']
    high_prio_folder = '.priority'

    def can_handle_command(self, command):
        return True if command in ['slice'] else False

    def handle_command(self, command, args):
        if command == 'slice':
            self.slice_image(source_image=self._make_absolute_path(args.picture),
                             tile_width=args.width, tile_height=args.height)

    def build_plugin_subparser(self, subparsers):
        parser_slice = subparsers.add_parser('slice', help='slice an image into tiles',
                                             description='slice an image into tiles to create a poster. \n'
                                                         + 'tiles need to be a multiple of 154x111 pixels '
                                                         + 'in order not to be cropped.')
        parser_slice.add_argument('picture',
                                  type=str,
                                  help='path to a picture to slice into tiles')

        parser_slice.add_argument('width',
                                  type=int,
                                  help='tile width')
        parser_slice.add_argument('height',
                                  type=int,
                                  help='tile height')

    def get_img_and_text(self, payload, cli_args):
        if not payload.get('folder'):
            self.logger.error("no folder set in configuration")
            exit(1)

        folder = self._make_absolute_path(payload.get('folder'))
        img_path = self._pick_image(folder)

        if not img_path:
            self.logger.error("no images in folder " + folder)
            exit(1)

        move_info = 'moving to sent folder' if payload.get('move') else 'no move'

        self.logger.info('choosing image {} ({})'.format(img_path, move_info))
        file = open(img_path, 'rb')

        if payload.get('move'):
            self._move_to_sent(folder, img_path)

        return {
            'img': file,
            'text': ''
        }

    def slice_image(self, source_image, tile_width, tile_height):
        if not os.path.isfile(source_image):
            self.logger.error('file {} does not exist'.format(source_image))
            exit(1)

        file = open(source_image, 'rb')
        with Image.open(file) as image:
            cwd = os.getcwd()
            basename = strftime("slice_%Y-%m-%d_%H-%M-%S", gmtime())
            directory = os.path.join(cwd, basename)

            self.logger.info('slicing picture {} into tiles'.format(source_image))
            tiles = make_tiles(image, tile_width=tile_width, tile_height=tile_height)
            store_tiles(tiles, directory)
            self.logger.info('picture sliced into {} tiles {}'.format(len(tiles), directory))

    def _pick_image(self, folder):
        candidates = []
        high_prio = os.path.join(folder, self.high_prio_folder)
        if os.path.exists(high_prio):
            for file in os.listdir(high_prio):
                for ext in self.supported_ext:
                    if file.lower().endswith(ext):
                        candidates.append(os.path.join(self.high_prio_folder, file))

        if not candidates:
            for file in os.listdir(folder):
                for ext in self.supported_ext:
                    if file.lower().endswith(ext):
                        candidates.append(file)

        if not candidates:
            self.logger.error("no images in folder " + folder)
            exit(1)

        img_name = random.choice(candidates)
        img_path = os.path.join(folder, img_name)
        return img_path

    def _move_to_sent(self, picture_folder, image_path):
        sent_folder = os.path.join(picture_folder, 'sent')
        if not os.path.exists(sent_folder):
            os.makedirs(sent_folder)
            self.logger.debug('creating folder {}'.format(sent_folder))

        img_name = self._get_filename(image_path)
        sent_img_path = os.path.join(sent_folder, img_name)
        os.rename(image_path, sent_img_path)
        self.logger.debug('moving image from {} to {}'.format(image_path, sent_img_path))

    def _get_filename(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def _make_absolute_path(self, path):
        if not os.path.isabs(path):
            return os.path.join(os.getcwd(), path)
        else:
            return path


def main():
    PostcardsFolder().main(sys.argv[1:])


if __name__ == '__main__':
    main()
