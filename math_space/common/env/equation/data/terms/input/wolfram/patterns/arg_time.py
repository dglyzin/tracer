from inspect import getsource


class ArgTime():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''

    def __init__(self, net):
        self.net = net
        self.id = 'arg_time'
        self.init_pattern()

    def init_pattern(self):

        #  find patterns like t-1.5:
        # self.arg_time = r"[t]-%s" % (self.term_delay)
        self.gen = lambda term_delay: r"[t](-%s)?" % (term_delay)

    def __call__(self):
        term_delay = self.net.terms['arg_delay']()
        return(self.gen(term_delay))

    def get_source(self):
        return(getsource(self.gen))
