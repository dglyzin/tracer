from functools import reduce


class Base():

    '''Used for create base pattern without dependency.
    Must be initiated before all other terms.'''

    def __init__(self, net):
        self.net = net
        self.id = 'base'
        self.init_patterns()

    def init_patterns(self):

        self.dep_vars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.coeffs = self.dep_vars.lower()[:-3]
        self.indep_vars = 'xyz'
        self.time_var = 't'

        params = self.dep_vars.lower()
        params = params.replace(self.time_var, "")
        for a in self.indep_vars:
            params = params.replace(a, "")
        self.params = params

        funcs = ['exp', 'sqrt', 'log',
                 'sin', 'cos', 'tan',
                 'sinh', 'tanh', 'f', 'g', 'h']
        self.funcs = funcs

        self.unary = ['-']
        self.binary = ['+', '-', '*', '/']

    def make_args(self, term_type):

        ''' Find patterns like "{x,1.5}", "{x,1.5}{y,1.1}", ...
        or "{x,1}", "{x,1}{y,3}", ...
        
        >>> re.search(args, "{x,1.5}{y,1.3}").groupdict()
        "{'val_x': '1.5', 'val_y': '1.1', 'val_z': None}"
        '''

        # (?P<val_x>1.5)
        term_val = lambda x: r"(?P<val_%s>%s)" % (x, term_type)

        # pointer to term with x (?P=val_x)
        # term_val_pointer = lambda x: r"(?P=val_%s>)" % (x)

        # {x,1.5} or {y,1.3} zero or one times:
        # >>> re.search(arg("x"),"{x,1.5}").group()
        # '{x,1.5}'
        arg = lambda x: r"(\{%s,%s\})?" % (x, term_val(x))

        # find patterns like "{x,1.5}", "{x,1.5}{y,1.1}", ...
        # >>> re.search(args, "{x,1.5}{y,1.3}").groupdict()
        # "{'val_x': '1.5', 'val_y': '1.1', 'val_z': None}"
        args = ("("
                + reduce(lambda acc, x: acc+x,
                         [arg(x) for x in self.indep_vars],
                         "")
                + ")")
        return(args)
