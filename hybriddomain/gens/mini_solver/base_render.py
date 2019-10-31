from jinja2 import Environment, FileSystemLoader


class GenBaseRend():
    
    def __init__(self, hd_dir=None):
        if hd_dir is not None:
            import os
            pathToTemplates = os.path.join(hd_dir,
                                           'gens/mini_solver/templates')
        else:
            pathToTemplates = 'gens/mini_solver/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate
