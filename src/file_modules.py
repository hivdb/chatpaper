import json
import sys
from importlib.abc import Loader
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_loader
import pkg_resources
from ruamel.yaml import YAML

yaml = YAML()


class YAMLLoader(Loader):

    def exec_module(self, module):
        pkg = '.'.join(module.__spec__.origin.split('.')[:-1])
        file_name = module.__spec__.origin.split('.')[-1]
        file_path = pkg_resources.resource_filename(pkg, file_name + '.yaml')

        with open(file_path) as fd:
            for k, v in yaml.load(fd).items():
                setattr(module, k, v)


class YAMLFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        # TODO: only the local folder can use this importer
        return spec_from_loader(fullname, YAMLLoader(), origin=fullname)


sys.meta_path.append(YAMLFinder())
