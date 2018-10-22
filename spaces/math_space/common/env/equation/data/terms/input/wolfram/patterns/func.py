from functools import reduce
from inspect import getsource


class Func():
    
    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''

    def __init__(self, net):
        self.net = net
        self.id = 'func'
        self.init_pattern()

    def init_pattern(self):
        
        '''For sin(a)'''

        self.gen = (lambda funcs:
                    (r'(%s)\(' % (reduce(lambda acc, f: f + '|' + acc,
                                         funcs, "")[:-1])))
    
    def __call__(self):
        funcs = self.net.terms['base'].funcs
        return(self.gen(funcs))

    def get_source(self):
        return(getsource(self.gen))
