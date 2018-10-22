from env.equation.data.terms.args.extractor import ArgsGen


class EqArgs():

    def __init__(self, net):
        self.net = net

    def subs(self, **kargs):
        for var_name in kargs:
            for var in self.net.vars:
                if var['variable']['name'] == var_name:
                    val = kargs[var_name]
                    var['variable']['value'] = val
                    for node in var['nodes']:
                        node.args['variable'] = var['variable']
                    # break
    
    def get_vars(self):

        '''Extract variables from arguments.
        For term func variable is if name of term is len 1
        (ex: f, g, h, ...).
        It also add var key to args.'''

        terms_vars = ['free_var', 'var', 'func', 'coeffs', 'idx']
        terms_br = ['func', 'idx']
        try:
            self.net.args
        except AttributeError:
            self.get_args()

        self.net.vars = []
        for arg in self.net.args:
            if arg['id']['term_id'] in terms_vars:
                # special for term func
                if arg['id']['term_id'] in terms_br:
                    if len(arg['id']['name'][:-1]) == 1:
                        # for func and idx variables only f, g, h...
                        arg['variable'] = {'name': arg['id']['name'][:-1]}
                        for node in arg['nodes']:
                            node.args['variable'] = arg['variable']
                        self.net.vars.append(arg)
                else:
                    if "(" in arg['id']['name']:
                        raise(BaseException("Variables with brackets"
                                            + " not supported (like U())"))
                    arg['variable'] = {'name': arg['id']['name']}
                    for node in arg['nodes']:
                        node.args['variable'] = arg['variable']
                    self.net.vars.append(arg)
    
    def get_args(self):
        # TODO
        gen = ArgsGen()
        self.net.tree.map_out(gen)
        self.net.args = gen.args

    '''
    def get_args(self):

        ''Extract variables from tree.
        For now only work with func_pattern and free_var_pattern

        Example:
        for f(x+y) make self.args for f, x, y.
        They must be alredy recognized by lex.
        it add simple rand_gen to each self.args, that
        used to generate it's values (in self.sampling method).

        It also add sympy_gen attr for vars and constants.
        (for correct call eval(eq) method).

        Example:
        >>> e = Equation('f(x+y+x)+f(x)+g(z)')
        >>> e.parse()
        # create rand_gen:
        >>> e.flatten('sympy')
        # use create args with use of rand_gen:
        >>> e.get_args()
        >>> e.args
        {'f': func_pattern, rand: cos(, nodes count: 2,
         'g': func_pattern, rand: sin(, nodes count: 1,
         'x': free_var_pattern, rand: 0.9204389089496596, nodes count: 3,
         'y': free_var_pattern, rand: 0.08279757240786934, nodes count: 1,
         'z': free_var_pattern, rand: 0.3454996936754938, nodes count: 1}
        ''
        self.args = {}

        class Arg():

            # ''Represent arguments of sent with they data.
            # f(x+y)-> f, x, y''

            def __init__(self, name, pattern, node,
                         rand_gen=None, sympy_gen=None, val_fix=None):
                self.name = name
                self.pattern = pattern
                if rand_gen is not None:
                    self.rand_gen = rand_gen
                if sympy_gen is not None:
                    self.sympy_gen = sympy_gen
                if val_fix is not None:
                    self.val_fix = val_fix

                self.nodes = [node]

            def __repr__(self):
                s = "%s, nodes count: %s" % (str(self.pattern),
                                             str(len(self.nodes)))
                try:
                    s = s + " rand: %s" % (str(self.rand_gen()))
                except AttributeError:
                    pass
                try:
                    s = s + " sympy: %s" % (self.sympy_gen)
                except AttributeError:
                    pass
                try:
                    s = s + " val_fix: %s" % (self.val_fix)
                except AttributeError:
                    pass

                return(s)

        for node in self.eq_tree:
            try:
                val, _, pattern = node.name.lex
            except AttributeError:
                continue
            try:
                rand_gen = node.arg_rand
            except AttributeError:
                rand_gen = None
            try:
                sympy_gen = node.arg_sympy
            except AttributeError:
                sympy_gen = None
            try:
                val_fix = node.arg_fix
            except AttributeError:
                val_fix = None

            if (rand_gen is None and sympy_gen is None
                and val_fix is None):
                continue
            if val in self.args.keys():
                self.args[val].nodes.append(node)
            else:
                self.args[val] = Arg(val, pattern, node,
                                     rand_gen, sympy_gen, val_fix)
    '''
    
