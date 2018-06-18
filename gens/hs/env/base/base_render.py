from jinja2 import Environment, FileSystemLoader


class GenBaseRend():
    
    def __init__(self):
        pathToTemplates = 'gens/hs/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate
