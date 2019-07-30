from inspect import getsource


class ArgInt():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''

    def __init__(self, net):
        self.net = net
        self.id = 'int'
        self.init_patterns()

    def init_patterns(self):
        
        self.gen = lambda: r"\d+"

    def __call__(self):
        
        return(self.gen())

    def get_source(self):
        return(getsource(self.gen))
