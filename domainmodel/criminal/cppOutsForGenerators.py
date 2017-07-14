from jinja2 import Environment, FileSystemLoader


class CppOutsForGenerators():
    '''
    DESCRIPTION:

    '''
    def __init__(self):
        # self.params = params
        pathToTemplates = 'domainmodel/criminal/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate
       
    def get_out_for_initials(self, params):
        template = self.env.get_template('initial_conditions.template')

        args = {
            'blocks': params.blocks,
            'initials': params.initials,
            'bounds': params.bounds,
            'enumerate': enumerate,
            'len' : len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

        
