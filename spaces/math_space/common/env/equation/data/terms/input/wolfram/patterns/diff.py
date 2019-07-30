from inspect import getsource


class Diff():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'diff'
        self.init_pattern()

    def init_pattern(self):

        ''' For
        D[U(t-5.1),{y,2}]
        D[U,{x,1}]
        in begining of sent.
        '''
        
        # for D[U,{x,2}] or D[U(t-1.1),{x,1}{y,3}]
        # In [96]: re.search(g.diff_pattern,"D[U(t-1),{x,1}{y,3}]").groupdict()
        # Out[96]: {'delay': '1', 'val_x': '1', 'val_y': '3', 'val_z': None}
        #diff_pattern = ('^D\[[%s](\(%s\))?,%s\]'
        #                % (self.dep_vars, self.arg_time, self.args_ord))
        # diff_pattern = ('D\[[%s](\(%s\))?,%s\]'
        #                % (self.dep_vars, self.arg_time, self.args_ord))
        self.gen = lambda var, args_ord: ('D\[%s,%s\]'
                                          % (var, args_ord))
        
    def __call__(self):
        term_var = self.net.terms['var']()
        term_int = self.net.terms['int']()
        args_ord = self.net.terms['base'].make_args(term_int)
        return(self.gen(term_var, args_ord))

    def get_source(self):
        return(getsource(self.gen))
