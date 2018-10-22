from inspect import getsource


class Bdp():

    '''init_pattern used for create pattern generator
    __call__ used for getting term pattern with generator
    before using __call__ all terms in net must be initiated'''
    
    def __init__(self, net):
        self.net = net
        self.id = 'bdp'
        self.init_pattern()

    def init_pattern(self):

        ''' For "V(t-1.1,{x,1.3})" in begining of sent'''

        # find V(t-1.1,{x,1.3}) in begining of sent:
        # >>> re.search(bound_delay_point, "V(t-1.1,{x,1.3})").group()
        # 'V(t-1.1,{x,1.3})'
        #bound_delay_point = (r"^[%s]\(%s,%s\)"
        #                     % (self.dep_vars, self.arg_time, self.args_space))
        # var_pattern used only as U (not U(t-1.1)).
        self.gen = (lambda var_bdp, arg_time, args_space:
                    (r"%s\(%s,%s\)" % (var_bdp, arg_time, args_space)))
        
    def __call__(self):

        term_float = self.net.terms['float']()
        var_bdp = self.net.terms['var_bdp']()
        arg_time = self.net.terms['arg_time']()
        args_space = self.net.terms['base'].make_args(term_float)
        return(self.gen(var_bdp, arg_time, args_space))

    def get_source(self):
        return(getsource(self.gen))
