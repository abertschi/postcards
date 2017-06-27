from postcards import Postcards
import sys
import os
import random
import ntpath


class FolderPlugin(Postcards):
    supported_ext = ['.jpg', '.jpeg', '.png']

    def get_img_and_text(self, payload):
        if not payload['folder']:
            raise Exception("No folder set in payload in config.json")

        folder = payload['folder']
        if not os.path.isabs(folder):
            abs_dir = os.path.dirname(os.path.realpath(__file__))
            folder = os.path.join(abs_dir, folder)

        candidates = []
        for file in os.listdir(folder):
            for ext in self.supported_ext:
                if file.endswith(ext):
                    candidates.append(file)

        if not candidates:
            print("No images in folder " + folder)
            exit(0)

        img_name = random.choice(candidates)
        img_path = os.path.join(folder, img_name)
        f = open(img_path, 'rb')

        if payload['move']:
            sent_folder = os.path.join(folder, 'sent')
            if not os.path.exists(sent_folder):
                os.makedirs(sent_folder)

            img_name = self.path_leaf(img_path)
            sent_img_path = os.path.join(sent_folder, img_name)
            os.rename(img_path, sent_img_path)

        return {
            'img': f,
            'text': ''
        }

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)


if __name__ == '__main__':
    FolderPlugin().execute(sys.argv[1:])
