from inspect import getsource


class Coeffs():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'coeffs'
        self.init_pattern()

    def init_pattern(self):
        self.gen = lambda coeffs: ('[%s]' % (coeffs))
        
    def __call__(self):
        coeffs = self.net.terms['base'].coeffs
        return(self.gen(coeffs))

    def get_source(self):
        return(getsource(self.gen))
