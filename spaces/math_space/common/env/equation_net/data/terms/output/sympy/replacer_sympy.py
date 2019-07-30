from translator.replacer.net_replacer import NetGen
from translator.replacer.replacer_brackets_patterns import BracketsNet as BrTermsGens

# from env.equation.data.terms.output.sympy.patterns \
#         .brackets.brackets_main import BracketsNet as BrTermsGens

'''
from env.equation.data.terms.output.sympy.patterns.diff import Diff
from env.equation.data.terms.output.sympy \
        .patterns.diff_time_var import DiffTimeVar
from env.equation.data.terms.output.sympy.patterns.var import Var
from env.equation_net.data.terms.output.sympy.patterns.default import Default
'''

import logging

# create logger
log_level = logging.INFO  # logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger('replacer_sympy.py')
logger.setLevel(level=log_level)


# terms_gens_cls = [Diff, Var, DiffTimeVar, Default]


class Out():
    pass


class Params():
    pass


class SympyGen(NetGen):

    '''Fill term.sympy with print_sympy,
    term.arg_rand (or term.arg_fix) with get_args_rand,
    term.arg_sympy with get_args
    and term.lambda_sympy with lambdify
    '''

    def get_terms_gen_cls(self):
        terms_gens_cls = (self.patterns_editor
                          .load_patterns("sympy", brackets=False))
        
        return(terms_gens_cls)

    def get_terms_br_gen_cls(self):

        '''return instance, run after
        ``self.patterns_editor`` initiated '''

        return(BrTermsGens(self, "sympy"))

    '''
    def get_terms_gen_cls(self):
        return(terms_gens_cls)

    def get_terms_br_gen_cls(self):
        return(BrTermsGens)
    '''

    def postproc(self, node):
        pass

    '''
    def translate_brackets(self, node):
        
        # ''Add to brackets like term''

        self.init_output((node))

        # add out to node:
        self.terms_br_gens(node)

        # left_term = self.lambdify(left_term)
        # left_term = self.get_args_rand(left_term)

    def translate(self, node):

        # ''Add pattern out to term and return it''

        self.init_output((node))

        self.print_out(node)
        # term = self.lambdify(term)
        # term = self.get_args(term)
        # term = self.get_args_rand(term)
    '''

    # FOR flatten
    def get_extractor(self, key="original"):
        if key == "sympy":
            return(self.extractor_sympy)
        return(NetGen.get_extractor(self, key))

    def extractor_sympy(self, node_idd):
        
        out = self.get_output_out(node_idd)
        if out is None:
            out = self.get_node_type(node_idd)
        return(out)
    # END FOR

    def init_output(self, nodes_idds):

        '''For add out to nodes'''

        for node_idd in nodes_idds:
            node = self.get_node(node_idd)
                            
            if node["data"] is None:
                node["data"] = {}
            try:
                node["data"]["output"]
            except KeyError:
                node["data"]["output"] = {}
            node["data"]["output"]["sympy"] = {}
            node["data"]["output"]["sympy"]["global_data"] = {}

    # def set_output_lambda(self, node, value):
    #     node.output.sympy.slambda = value

    def get_output_out(self, node_idd):

        node = self.get_node(node_idd)

        try:
            data = node["data"]["output"]["sympy"]["out"]
        except (KeyError, TypeError):
            return(None)
        return(data)

    def set_output_out(self, node_idd, value):
        node = self.get_node(node_idd)
        # print("node:")
        # print(node)
        if value is not None:
            node["data"]["output"]["sympy"]["out"] = value

    def get_output_data(self, node_idd):

        node = self.get_node(node_idd)

        try:
            data = node["data"]["output"]["sympy"]["global_data"]
        except (KeyError, TypeError):
            return(None)
        return(data)

    def set_output_data(self, node_idd, key, value):
        node = self.get_node(node_idd)
        node["data"]["output"]["sympy"]["global_data"][key] = value

    def get_params_field_name(self):
        return('term_print_sympy_params')

    '''
    def get_args_rand(self, term):

        ''Add random generator (arg_rand) to some term
        or arg_fix if term is float''

        try:
            val, _, pattern = term.name.lex
        except AttributeError:
            return(term)
            
        if pattern == 'func':
            val = val[:-1]

            def rand_gen():
                return(str(random.choice(['sin(', 'cos('])))
            term.arg_rand = rand_gen
        elif pattern == 'free_var':
            def rand_gen():
                return(float("%.3f" % random.random()))
            term.arg_rand = rand_gen
        elif pattern == 'coefs':
            def rand_gen():
                return(float("%.3f" % random.random()))
            term.arg_rand = rand_gen

        elif pattern == 'float':
            
            term.arg_fix = float(val)

        return(term)
    '''
    '''
    def get_args_old(self, term):

        ''Add arg_sympy to arg like terms (const, variables).''

        try:
            var = term.name.lex[0]
            pattern = term.name.lex[-1]
            if pattern == 'free_var':

                # transform to sympy:
                term.arg_sympy = sympy.symbols(names=var)
            elif (pattern == 'diff'
                  or pattern == 'diff_time'):

                reg_pattern = term.name.lex[1]

                # diff var (U):
                var = reg_pattern.group('val')
                # sympy_gen = "%s = sympy.symbols('%s')" % (var[0], var[0])
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'var':
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'free_var':
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'coefs':
                term.arg_sympy = sympy.randprime(1, 7)
            # todo
            #elif pattern == 'pow':
            #    term.arg_sympy = 
        except AttributeError:
            pass
        return(term)
    '''
    '''
    def lambdify(self, node):

        ''Add lambda expresion to some terms
        lambda_sympy if term is func (include +,-,*,/)
        arg_sympy if term is var (U,).
        ''

        term_value = self.get_term_value(node)
        if term_value == '+':
            self.set_output_lambda(node, lambda L, R: L.__add__(R))
            # node.lambda_sympy = lambda L, R: L.__add__(R)
        elif term_value == '*':
            self.set_output_lambda(node, lambda L, R: L.__mul__(R))
            # node.lambda_sympy = lambda L, R: L.__mul__(R)
        elif term_value == '-':
            self.set_output_lambda(node, lambda L, R: R.__add__(-L))
            # node.lambda_sympy = lambda L, R: R.__add__(-L)
        elif term_value == '/':
            self.set_output_lambda(node, lambda L, R: R.__div__(L))
            # node.lambda_sympy = lambda L, R: R.__div__(L)
        
        elif term_value == '=':
            self.set_output_lambda(node, lambda L, R: L.__eq__(R))
            # node.lambda_sympy = lambda L, R: L.__eq__(R)
        elif term_value == '=-':
            self.set_output_lambda(node, lambda L, R: L.__eq__(-R))
            # node.lambda_sympy = lambda L, R: L.__eq__(-R)

        try:
            term_id = self.get_term_id(node)
            # term_id = node.name.lex[-1]
            if term_id == 'func':
                if 'variable' in node.args:
                    func = node.args['variable']['value']
                else:
                    # func = node.name.lex[0][:-1]
                    func = self.get_term_value(node)[:-1]
                self.set_output_lambda(node, lambda A: sympy.simplify(func)(A))
                # node.lambda_sympy = lambda A: sympy.simplify(func)(A)
            ''
            elif term_id in ['var', 'free_var', 'coeffs']:
                var = node.args['variable']['value']
                # var = node.name.lex[0]

                # transform to sympy:
                self.set_output_lambda(node, lambda: var)
                # node.arg_sympy = sympy.symbols(names=var)
                # node.lambda_sympy = lambda: sympy.symbols(names=var)
            ''
        except AttributeError:
            pass
        return(node)
    '''
    '''
    def print_out(self, node):

        try:
            node.output
        except AttributeError:
            node.output = Out()

        node.output.sympy = Out()
        node.output.sympy.global_data = {}
        # node.output.sympy.local_data = {}

        # find generator for node:
        term_id = node.name.lex[-1]
        if term_id is None or term_id not in self.terms_gens:
            term_id = 'default'

        # add out:
        self.terms_gens[term_id](node)
    '''
    def set_dim(self, **kwargs):
        self.dim = kwargs['dim']
