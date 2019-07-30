from inspect import getsource


class Dot():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'dot'
        self.init_pattern()

    def init_pattern(self):
        '''
        For re.search("(\.\w+\((\w+)?\))+", "A.fdad3(a).si(f)")
        re.search("(\.\w+(?P<call>\((?P<arg>\w+)?\))?)+", "A.fdad3(g).si(f)")
        re.search("(?P<obj>\w+)(\.\w+(?P<call>\((?P<arg>\w+)?\))?)+",
                  "A.fdad3(g).si(f)")
        '''
        
        self.obj = "(?P<obj>\w+)"
        self.arg = "(?P<arg>\w+)?"

        # find ()
        self.call = "(?P<call>\(%s\))?" % (self.arg)
    
        # find a.t, a.t(), a.t(), a.t().c()
        # but not a.1(), a.1:
        self.main = r"%s(\.([a-zA-Z])+%s)+" % (self.obj, self.call)
        
        self.gen = lambda: self.main

    def __call__(self):
        return(self.gen())

    def get_source(self):
        return(getsource(self.gen))
