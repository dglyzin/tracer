from inspect import getsource


class ArgFloat():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''

    def __init__(self, net):
        self.net = net
        self.id = 'float'
        self.init_patterns()
        
    def init_patterns(self):

        # 1.5 or 1:
        self.gen = lambda: r"\d+\.\d+|\d+"

    def __call__(self):
        return(self.gen())

    def get_source(self):
        return(getsource(self.pattern))

