from math_space.common.equation.replacer.replacer import Gen
import sympy
import random


import logging

# create logger
log_level = logging.INFO  # logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger('replacer_cpp.py')
logger.setLevel(level=log_level)


class Out():
    pass


class SympyGen(Gen):

    '''Fill term.sympy with print_cpp,
    term.arg_rand (or term.arg_fix) with get_args_rand,
    term.arg_sympy with get_args
    and term.lambda_sympy with lambdify
    '''

    def __init__(self):
        pass

    def postproc(self, node):
        pass

    def translate_brackets(self, left_term, right_term):
        
        '''Add to brackets like term'''
        
        left_term = self.print_sympy(left_term)

        left_term = self.lambdify(left_term)
        left_term = self.get_args_rand(left_term)

        return((left_term, right_term))

    def add_out_to(self, term):

        '''Add pattern out to term and return it'''

        term = self.print_sympy(term)
        term = self.lambdify(term)
        term = self.get_args(term)
        term = self.get_args_rand(term)

        return(term)

    def get_args_rand(self, term):

        '''Add random generator (arg_rand) to some term
        or arg_fix if term is float'''

        try:
            val, _, pattern = term.name.lex
        except AttributeError:
            return(term)
            
        if pattern == 'func_pattern':
            val = val[:-1]

            def rand_gen():
                return(str(random.choice(['sin(', 'cos('])))
            term.arg_rand = rand_gen
        elif pattern == 'free_var_pattern':
            def rand_gen():
                return(float("%.3f" % random.random()))
            term.arg_rand = rand_gen
        elif pattern == 'coefs_pattern':
            def rand_gen():
                return(float("%.3f" % random.random()))
            term.arg_rand = rand_gen

        elif pattern == 'float_pattern':
            
            term.arg_fix = float(val)

        return(term)

    def get_args(self, term):

        '''Add arg_sympy to arg like terms (const, variables).'''

        try:
            var = term.name.lex[0]
            pattern = term.name.lex[-1]
            if pattern == 'free_var_pattern':

                # transform to sympy:
                term.arg_sympy = sympy.symbols(names=var)
            elif (pattern == 'diff_pattern'
                  or pattern == 'diff_time_var_pattern'):

                reg_pattern = term.name.lex[1]

                # diff var (U):
                var = reg_pattern.group('val')
                # sympy_gen = "%s = sympy.symbols('%s')" % (var[0], var[0])
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'var_pattern':
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'free_var_pattern':
                term.arg_sympy = sympy.symbols(names=var)
            elif pattern == 'coefs_pattern':
                term.arg_sympy = sympy.randprime(1, 7)

        except AttributeError:
            pass
        return(term)

    def lambdify(self, term):

        '''Add lambda expresion to some terms'''

        if term.name == '+':
            term.lambda_sympy = lambda L, R: L.__add__(R)
        elif term.name == '*':
            term.lambda_sympy = lambda L, R: L.__mul__(R)
        elif term.name == '-':
            term.lambda_sympy = lambda L, R: R.__add__(-L)
        elif term.name == '/':
            term.lambda_sympy = lambda L, R: R.__div__(L)
        
        elif term.name == '=':
            term.lambda_sympy = lambda L, R: L.__eq__(R)
        elif term.name == '=-':
            term.lambda_sympy = lambda L, R: L.__eq__(-R)

        try:
            pattern = term.name.lex[-1]
            if pattern == 'func_pattern':
                func = term.name.lex[0][:-1]
                term.lambda_sympy = lambda A: sympy.simplify(func)(A)
            elif (pattern == 'free_var_pattern'
                  or pattern == 'coefs_pattern'):
                var = term.name.lex[0]

                # transform to sympy:
                term.arg_sympy = sympy.symbols(names=var)

        except AttributeError:
            pass
        return(term)

    def print_sympy(self, term):
        '''
        term.lex = ['D[U,{x,2}]', <_sre.SRE_Match object>, 'diff_pattern']
        add out to term
        transform term to sympy.
        extract data from pattern (if any exist for such pattern)
        and add it to term.
        
        '''
        pattern = term.name.lex[-1]
        logger.debug("pattern")
        logger.debug(pattern)
        if pattern == 'diff_pattern':

            reg_pattern = term.name.lex[1]
            
            # diff var (U):
            var = reg_pattern.group('val')
            
            # find diff orders (free_var: x, order: 1):
            for free_var in 'xyz':
                order = reg_pattern.group('val_'+free_var)
                if order is not None:
                    break
                    
            # add args x, y to var:
            var = self._add_args(var)
            
            # transform to sympy:
            term.sympy = "sympy.diff(%s, %s, %s)" % (var, free_var, order)

        elif pattern == 'diff_time_var_pattern':
            
            reg_pattern = term.name.lex[1]
            
            # diff var (U):
            var = reg_pattern.group('val')

            # add args x, y to var:
            var = self._add_args(var)
            
            # transform to sympy:
            term.sympy = "sympy.diff(%s, t)" % (var)

        elif pattern == 'var_pattern':
            
            reg_pattern = term.name.lex[1]
            
            # diff var (U):
            var = reg_pattern.group('val')

            # add args x, y to var:
            var = self._add_args(var)
            
            # transform to sympy:
            term.sympy = var
        elif pattern == 'func_pattern':
            
            func = term.name.lex[0]
            logger.debug("func_pattern:")
            logger.debug(func)

            # transform to sympy:
            term.sympy = "sympy.%s" % (func)

        return(term)

    def _add_args(self, var):
        
        '''Add x, y to var'''

        # FOR add args to var:
        if self.dim == 1:
            x = ', x)'
        elif self.dim == 2:
            x = ', x, y)'

        # U(t-1)
        if '(' in var:
            var = var[:-1] + x
        else:
            var = var + '(' + 't'+x
        # END FOR
        
        return(var)
        
    def set_dim(self, **kwargs):
        self.dim = kwargs['dim']
