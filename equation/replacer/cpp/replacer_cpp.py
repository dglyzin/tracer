from replacer.cpp.cpp_out import Params
from replacer.cpp.cpp_out import Diff, Var, FreeVar
from replacer.cpp.cpp_out import Coeffs, Bdp, Pow, Func
from replacer.cpp.cpp_out import delay_postproc
from replacer.replacer import Gen


import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('replacer_cpp.py')
logger.setLevel(level=log_level)


class Out():
    pass


class CppGen(Gen):
    def __init__(self):
        # TODO differ delays for differ U, V:
        self.global_params = Params()
        self.global_params.delays_owner_id = 0
        self.global_params.delays = {}
        
        self.diff_gen = Diff(self)
        self.bdp_gen = Bdp(self)
        self.var_gen = Var(self)
        self.free_var_gen = FreeVar(self)
        self.coeffs_gen = Coeffs(self)
        self.pow_gen = Pow(self)
        self.func_gen = Func(self)

    def postproc(self, node):
        delay_postproc(node)

    def translate_brackets(self, left_term, right_term):
        # TODO
        left_term.cpp = Out()
        right_term.cpp = Out()

        # for pow (left=( right=w)
        if right_term.name == 'w':
            logger.debug(right_term)
            self.pow_gen.set_base(right_term)
            # transform to cpp:
            left_out, right_out = self.pow_gen.print_cpp()
            left_term.cpp.out = left_out
            right_term.cpp.out = right_out

        # for f (left=f right=))
        if left_term.name == 'f':
            logger.debug(left_term)
            self.func_gen.set_base(left_term)
            # transform to cpp:
            left_out, right_out = self.func_gen.print_cpp()
            left_term.cpp.out = left_out
            right_term.cpp.out = right_out

        return((left_term, right_term))

    def add_out_to(self, term):

        '''Add pattern out to term and return it'''

        term = self.print_cpp(term)
        return(term)

    def print_cpp(self, term):
        '''
        term.lex = ['D[U,{x,2}]', <_sre.SRE_Match object>, 'diff_pattern']
        add out to term
        transform term to cpp.
        extract data from pattern (if any exist for such pattern)
        and add it to term.
        
        '''
        term.cpp = Out()
        term.cpp.global_data = {}
        pattern = term.name.lex[-1]
        if pattern == 'diff_pattern':
            # add data to term:
            data = self.diff_gen.set_base(term)
            if data is not None:
                term.cpp.global_data = data

            # transform to cpp:
            term.cpp.out = self.diff_gen.print_cpp()

        elif pattern == 'bdp':
            # add data to term:
            data = self.bdp_gen.set_base(term)
            if data is not None:
                term.cpp.global_data = data

            # transform to cpp:
            term.cpp.out = self.bdp_gen.print_cpp()

        elif pattern == 'var_pattern':
            # add data to term:
            data = self.var_gen.set_base(term)
            if data is not None:
                term.cpp.global_data = data

            # transform to cpp:
            term.cpp.out = self.var_gen.print_cpp()

        elif pattern == 'free_var_pattern':
            
            # extract var name:
            self.free_var_gen.set_base(term)

            # transform to cpp:
            term.cpp.out = self.free_var_gen.print_cpp()

        elif pattern == 'coefs_pattern':
            # extract coeffs value from term
            # and replace it by index:
            self.coeffs_gen.set_coeff_index(term)

            # transform to cpp:
            term.cpp.out = self.coeffs_gen.print_cpp()
        
            '''
            elif pattern == 'pow_pattern':
                # transform to cpp:
                term.cpp.out = None
            elif pattern == 'func_pattern':
                # transform to cpp:
                term.cpp.out = term.lex[0]
            '''

        elif pattern == 'float_pattern':
            # transform to cpp:
            term.cpp.out = term.name.lex[0]
        else:
            term = self.default_action(term)
        return(term)

    def default_action(self, term):
        term.cpp.out = term.name.lex[0]
        return(term)

    def set_dim(self, **kwargs):
        self.bdp_gen.set_dim(kwargs['dim'])

    def set_point(self, **kwargs):
        self.bdp_gen.set_point(kwargs['point'])

    def set_blockNumber(self, **kwargs):
        self.diff_gen.set_blockNumber(kwargs['blockNumber'])
        self.bdp_gen.set_blockNumber(kwargs['blockNumber'])

    def set_diff_type(self, **kwargs):
        self.diff_gen.set_diff_type(**kwargs)

    def set_vars_indexes(self, **kwargs):
        # int: shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        map_vti = dict(kwargs['vars_to_indexes'])
        self.diff_gen.set_vars_indexes(map_vti)
        self.var_gen.set_vars_indexes(map_vti)
        self.bdp_gen.set_vars_indexes(map_vti)

    def set_coeffs_indexes(self, **kwargs):
        # map  coeffs ot it's index
        # like (a,b)-> (params[+0], params[+1])
        map_cti = dict(kwargs['coeffs_to_indexes'])
        self.coeffs_gen.set_coeffs_indexes(map_cti)


def test():

    import lex

    class term():
        pass

    # FOR diff pattern:
    t = term()
    l = lex.Lex()
    res = lex.re.search(l.diff_pattern, 'D[U(t-1.1),{x,2}]')
    t.lex = [res.string, res, 'diff_pattern']
    print('term.lex:')
    print(t.lex)

    gen = CppGen()
    gen.set_varIndex(varIndex=0)
    gen.set_blockNumber(blockNumber=0)

    gen.set_diff_type(diffType='pure', diffMethod='common')

    gen.add_out_to(t)
    print(t.cpp_out)
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)

    gen.set_diff_type(diffType='pure', diffMethod='special',
                      side=0, func='sin')

    gen.add_out_to(t)
    print(t.cpp_out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)

    gen.set_diff_type(diffType='pure', diffMethod='interconnect',
                      side=0, firstIndex=0, secondIndexSTR=1)

    gen.add_out_to(t)
    print(t.cpp_out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR

    # FOR Val pattern
    t = term()
    l = lex.Lex()
    res = lex.re.search(l.var_pattern, 'U')
    t.lex = [res.string, res, 'var_pattern']
    print('term.lex:')
    print(t.lex)

    gen.set_varIndex(varIndex=0)
    gen.add_out_to(t)
    print(t.cpp_out)
    # END FOR

    # FOR coeffs pattern
    t = term()
    l = lex.Lex()
    res = lex.re.search(l.coefs_pattern, 'a')
    t.lex = [res.string, res, 'coefs_pattern']
    print('term.lex:')
    print(t.lex)

    gen.set_coeffsIndex(coeffsIndex=0)
    gen.add_out_to(t)
    print(t.cpp_out)
    # END FOR

    # FOR bound pattern 1d
    t = term()
    l = lex.Lex()
    print(l.patterns_dict['bdp'])
    res = lex.re.search(l.patterns_dict['bdp'], 'U(t-1.1,{x,0.3})')
    t.lex = [res.string, res, 'bdp']
    print('term.lex:')
    print(t.lex)

    gen.set_dim(dim=1)
    gen.set_point(point=[3])
    gen.add_out_to(t)
    print(t.cpp_out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR

    # FOR bound pattern 2d
    t = term()
    l = lex.Lex()
    res = lex.re.search(l.patterns_dict['bdp'], 'U(t-1.1,{x,0.3}{y,0.3})')
    t.lex = [res.string, res, 'bdp']
    print('term.lex:')
    print(t.lex)

    gen.set_dim(dim=2)
    gen.set_point(point=[3, 3])
    gen.add_out_to(t)
    print(t.cpp_out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR
    

if __name__ == '__main__':
    test()
