from env.equation.sampling.sympy.sampling_sympy_main import SamplingSympy

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('equation.eq_sampling')

# if using directly uncoment that:
# create logger
'''
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('eq_sampling')
logger.setLevel(level=log_level)
'''


class EqSampling():

    def __init__(self, net):
        self.net = net
        self.sympy = SamplingSympy(self)

    def sampling_subs(self, rand_terms_gens):
        
        '''Sampling using subs'''

        try:
            self.net.vars
        except AttributeError:
            self.net.args_editor.get_vars()

        subs_args = {}
        for var in self.net.vars:
            term_id = var['id']['term_id']
            var_name = var['variable']['name']

            if term_id in rand_terms_gens:
                term_value = rand_terms_gens[term_id]()
                subs_args[var_name] = term_value
        logger.info(subs_args)
        self.net.args_editor.subs(**subs_args)
     
    def sampling_vars(self, rand_terms_gens):

        '''Sampling using vars'''

        try:
            self.net.vars
        except AttributeError:
            self.net.args_editor.get_vars()

        for var in self.net.vars:
            term_id = var['id']['term_id']
            if term_id in rand_terms_gens:
                if 'variable' in var:
                    var['variable']['value'] = rand_terms_gens[term_id]()
                    for node in var['nodes']:
                        node.args['variable']['value'] = var['variable']['value']

    def sampling_old(self):

        '''Generate value for each arg in self.args.
        Used self.args[val].rand_gen for each value. (default is
        set in Equation.get_args)
        If insted of rand_gen has attribute arg_fix, it's value will
        be used instead.
        After that Equation.flatten('rand') can be used to generate
        whole equation.
        Or Equation.lambdify to sample equation.

        Example:
        >>> e = Equation("f(x+y)")
        >>> e.parse()
        >>> e.sampling()
        >>> e.flatten('rand')
        sin(0.2699527968481269+0.6823613609913871+0.2699527968481269)
        >>> e.sampling()
        >>> e.flatten('rand')
        sin(0.7021609513068388+0.9301007659964816+0.7021609513068388)
        '''

        for arg_key in self.args.keys():
            try:
                val = self.args[arg_key].rand_gen()
                for node in self.args[arg_key].nodes:
                    node.rand = val
            except AttributeError:
                # maybe arg has fix value:
                try:
                    val = self.args[arg_key].val_fix
                    for node in self.args[arg_key].nodes:
                        node.rand = val
                except AttributeError:
                    continue

