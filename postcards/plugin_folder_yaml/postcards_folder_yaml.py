#!/usr/bin/env python
# encoding: utf-8

from postcards.plugin_folder.postcards_folder import PostcardsFolder
import sys
import random
import ntpath
import os

import yaml


class PostcardsFolderYaml(PostcardsFolder):
    """
    Send postcards with images from a yaml config
    """

    def can_handle_command(self, command):
        return True if command in ['validate'] else False

    def handle_command(self, command, args):
        if command == 'validate':
            config = self._read_json_file(args.config_file[0], 'config')
            payload = config.get('payload')
            if not payload:
                self.logger.warn("error: config file does not contain payload")
                exit(-1)

            folder_path, yaml_path = self._validate_cli(payload, args)
            doc = self.validate_and_parse_yaml(folder_path, yaml_path)
            for d in doc:
                self.logger.info("> entry: {}".format(d))
            self.logger.info("validation is successful")


    def build_plugin_subparser(self, subparsers):
        parser = subparsers.add_parser('validate', help='validate yaml file',
                                       description='check that yaml file contains the proper format ' +
                                                   'and that all pictures referenced exist.')
        parser.add_argument('-c', '--config',
                            nargs=1,
                            required=True,
                            type=str,
                            help='location to the configuration file (default: ./config.json)',
                            default=[os.path.join(os.getcwd(), 'config.json')],
                            dest='config_file')

    def get_img_and_text(self, payload, cli_args):
        folder_path, yaml_path = self._validate_cli(payload, cli_args)
        document = self.validate_and_parse_yaml(folder_path, yaml_path)

        if len(document) == 0:
            self.logger.warn("nothing left to do, no more pictures in yaml file left.")
            exit(1)

        remove_yaml = payload.get("remove_yaml")
        if remove_yaml in [True, None]:
            text = document.pop(0)
            img_name = document.pop(0)
        else:
            self.logger.info("remove_yaml = False, do not remove entries form yaml")
            text = document[0]
            img_name = document[1]

        img_path = os.path.join(folder_path, img_name)
        self._write_back_yaml(document, yaml_path)

        move_info = 'moving to sent directory' if payload.get('move') else 'no move'
        self.logger.info('choosing image \'{}\' ({})'.format(img_path, move_info))
        self.logger.info('choosing text \'{}\''.format(text))

        file = open(img_path, 'rb')
        if payload.get('move'):
            self._move_to_sent(folder_path, img_path)

        return {
            'img': file,
            'text': text
        }

    def validate_and_parse_yaml(self, folder_path, yaml_path):
        """
        both paths are absolute
        :return: nothing, fails on invalidity
        """

        data = ''
        try:
            f = open(yaml_path, 'r')
            data = f.read()
            f.close()
        except Exception as e:
            self.logger.error("error: can not read yaml file {}".format(yaml_path))
            exit(-1)

        document = None
        self.logger.info("reading yaml file at {}".format(yaml_path))
        try:
            document = yaml.load(data, Loader=yaml.FullLoader)
        except Exception as e:
            self.logger.error("error: can not parse yaml file {}".format(yaml_path))
            exit(-2)
        pass

        if len(document) % 2 != 0:
            self.logger.error("error: uneven number of entries in yaml file.")
            exit(-3)

        i = 1
        while i < len(document):
            img_path = document[i]
            img_abs_path = os.path.join(folder_path, img_path)

            if not os.path.isfile(img_abs_path):
                self.logger.error(
                    "error: path entry {}: '{}' in yaml file does not exist on disk..".format(i, img_abs_path))
                exit(-4)

            i = i + 2

        return document

    def _validate_cli(self, payload, cli_args):
        if not payload.get('folder'):
            self.logger.error("no folder set in configuration")
            exit(1)

        folder_location = self._make_absolute_path(payload.get('folder'))
        if not os.path.isdir(folder_location):
            self.logger.error("picture directory '{}' does not exist".format(folder_location))
            exit(1)

        if not payload.get('yaml'):
            self.logger.error("no yaml file set in configuration")
            exit(1)

        yaml_location = self._make_absolute_path(payload.get('yaml'))
        if not os.path.isfile(yaml_location):
            self.logger.error("yaml file {} does not exist".format(yaml_location))
            exit(1)

        self.logger.debug("cli validation successful")
        return folder_location, yaml_location

    def _write_back_yaml(self, document, location):
        dump = yaml.dump(document)
        file = open(location, "w")
        file.write(dump)
        file.close()


def main():
    PostcardsFolderYaml().main(sys.argv[1:])


# def _tmp():
#     cards = PostcardsFolderYaml()
#     yaml = os.path.join(os.getcwd(), '../../tmp/test.yaml')
#     pic_path = os.path.join(os.getcwd(), '../../tmp')
#
#     cards.validate_and_parse_yaml(pic_path, yaml)


if __name__ == '__main__':
    main()
