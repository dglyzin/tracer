from inspect import getsource


class Var():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'var'
        self.init_pattern()

    def init_pattern(self):

        '''For U or U(t-1.5)
        For all vars pattern first symbol will be
        used to classify delays (U(t-1.1)->delay[U]=map(1.1)).'''

        self.gen = lambda dep_vars, arg_time: ('(?P<val>[%s](\(%s\))?)'
                                               % (dep_vars, arg_time))

    def __call__(self):
        dep_vars = self.net.terms['base'].dep_vars
        arg_time = self.net.terms['arg_time']()
        return(self.gen(dep_vars, arg_time))

    def get_source(self):
        return(getsource(self.gen))
