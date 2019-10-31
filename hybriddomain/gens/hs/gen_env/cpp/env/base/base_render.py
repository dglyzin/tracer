import os
from jinja2 import Environment, FileSystemLoader


class GenBaseRend():
    
    def __init__(self):
        pathToTemplates = 'hybriddomain/gens/hs/gen_env/cpp/templates'

        # FOR setuptools extract real paths:
        print("pathToTemplates:")
        print(pathToTemplates)
        print(os.getcwd())
        real_absolute_path_to_file = os.path.dirname(os.path.realpath(__file__))
        print(real_absolute_path_to_file)
        relative_path_to_file = os.path.sep.join(__package__.split('.'))
        print(relative_path_to_file)
        index = real_absolute_path_to_file.index(relative_path_to_file)
        hd_folder = real_absolute_path_to_file[:index]
        print(hd_folder)
        pathToTemplates_real = os.path.join(hd_folder, pathToTemplates)
        print(pathToTemplates_real)
        # END FOR

        self.env = Environment(loader=FileSystemLoader(pathToTemplates_real))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate
