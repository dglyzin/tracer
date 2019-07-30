from inspect import getsource


class Idx():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'idx'
        self.init_pattern()

    def init_pattern(self):
        '''
        For re.search("(?P<obj>\w+)\[(?P<idx>((\d)+|((\d)+,)+))\]",
                      "a[1,2,3,]")
        '''
        
        # find 1 or 1,1, or 11, 123, 1,:
        self.idx = "(?P<idx>((\d)+|((\d)+,)+))"

        # find a, aa, Aa:
        self.obj = "(?P<obj>\w+)"

        # find a[1,2,3,]:
        self.main = r"%s\[" % (self.obj)
        # self.main = r"%s\[%s\]" % (self.obj, self.idx)
        
        self.gen = lambda: self.main

    def __call__(self):
        return(self.gen())

    def get_source(self):
        return(getsource(self.gen))
