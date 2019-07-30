from inspect import getsource


class ArgDelay():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''

    def __init__(self, net):
        self.net = net
        self.id = 'arg_delay'
        self.init_patterns()

    def init_patterns(self):

        # (?P<delay>1.5)
        self.gen = lambda term_float: r"(?P<delay>%s)" % (term_float)

    def __call__(self):
        term_float = self.net.terms['float']()
        return(self.gen(term_float))

    def get_source(self):
        return(getsource(self.gen))
