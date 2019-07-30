from inspect import getsource


class FreeVar():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'free_var'
        self.init_pattern()

    def init_pattern(self):

        '''For x, y, z'''

        self.gen = lambda indep_vars: "[%s]" % (indep_vars)

    def __call__(self):
        indep_vars = self.net.terms['base'].indep_vars
        return(self.gen(indep_vars))

    def get_source(self):
        return(getsource(self.gen))
