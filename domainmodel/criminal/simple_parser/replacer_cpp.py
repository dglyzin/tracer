from cpp_out import Params
from cpp_out import Diff, Val, Coeffs, Bdp
from replacer import Gen
from copy import deepcopy as copy


class CppGen(Gen):
    def __init__(self):
        # TODO differ delays for differ U, V:
        self.global_params = Params()
        self.global_params.delays_owner_id = 0
        self.global_params.delays = {}
        
        self.diff_gen = Diff(self)
        self.bdp_gen = Bdp(self)
        self.val_gen = Val(self)
        self.coeffs_gen = Coeffs(self)

    def postproc(self, out):

        '''Convert delays for all term's that have it.
        out is a list of terms, each have or have not
        global_data['delay_data'] value.
        If have, it will be transformed into cpp corect
        order (for ex: [5.1, 1.5, 2.7]->[3, 1, 2])

        First it collect delays (and remember from whom)
        then convert them,
        finely replace them into it's term.out string.
        
        Examples:
        term.global_data['delay_data'] = (1, 'V(t-1.1)', '1.1')
        term.out = source[delay]
        term.out_new = source[coverted delay for 1.1]
        '''

        def convert_delays(delays):

            '''Convert float delay to int,
            according it's value.

            For ex:
            [5.1, 1.5, 2.7]->[3, 1, 2]
            '''
            # delays = copy(delays)
            delays.sort()
            sdelays = [delays.index(val)+1 for val in delays]
            print(sdelays)
            return(zip(delays, sdelays))

        print("FROM postproc")

        # FOR factorize terms delays for var:
        # res[val] = [(delay_0, term_id_0), ...]
        res = {}
        for term in out:
            if type(term) == str:
                continue
            try:
                delay_data = term.global_data['delay_data']
                term_id, var, delay = delay_data
                # U(t-1.1)->U
                var = var[0]
                if var in res.keys():
                    res[var][delay] = term_id
                else:
                    res[var] = {delay: term_id}
            except KeyError:
                pass
        print(res)
        # END FOR

        # FOR map float delays to it's source equivalent:
        # map_dsd: var -> delay, sdelay
        map_dsd = lambda var: convert_delays(list(res[var].keys()))
        
        # map_td: term_id -> source delay
        map_td = dict([(res[var][delay], sdelay) for var in res.keys()
                       for delay, sdelay in map_dsd(var)])
        print(map_td)
        # END FOR

        # FOR find terms for converted delay:
        out_new = []
        for term in out:
            try:
                if type(term) == str:
                    out_new.append(term)
                    continue
                # if delay
                # transform source[delay]->source[1]:
                delay_data = term.global_data['delay_data']
                term_id, var, delay = delay_data
                sdelay = map_td[term_id]
                term.out = term.out.replace('delay', str(sdelay))
                term.global_data['converted_delay'] = sdelay
                out_new.append(term)
            except KeyError:
                try:
                    # if no delay
                    # transform source[delay]->source[0]
                    term.out = term.out.replace('delay', str(0))
                    out_new.append(term)
                except AttributeError:
                    # if term not have out:
                    # (like +):
                    out_new.append(term)
        print([o.out for o in out_new if type(o) != str])
        return(out_new)

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
        term.global_data = {}
        pattern = term.lex[-1]
        if pattern == 'diff_pattern':
            # add data to term:
            data = self.diff_gen.set_base(term)
            if data is not None:
                term.global_data = data
            else:
                term.global_data = {}

            # transform to cpp:
            term.out = self.diff_gen.print_cpp()

        elif pattern == 'bdp':
            # add data to term:
            data = self.bdp_gen.set_base(term)
            if data is not None:
                term.global_data = data
            else:
                term.global_data = {}

            # transform to cpp:
            term.out = self.bdp_gen.print_cpp()

        elif pattern == 'val_pattern':
            # add data to term:
            data = self.val_gen.set_base(term)
            if data is not None:
                term.global_data = data
            else:
                term.global_data = {}

            # transform to cpp:
            term.out = self.val_gen.print_cpp()

        elif pattern == 'coefs_pattern':
            # extract coeffs value from term
            # and replace it by index:
            self.coeffs_gen.set_coeff_index(term)

            # transform to cpp:
            term.out = self.coeffs_gen.print_cpp()

        elif pattern == 'pow_pattern':
            # transform to cpp:
            term.out = None
        elif pattern == 'func_pattern':
            # transform to cpp:
            term.out = term.lex[0]

        elif pattern == 'float_pattern':
            # transform to cpp:
            term.out = term.lex[0]
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
        self.val_gen.set_vars_indexes(map_vti)
        self.bdp_gen.set_vars_indexes(map_vti)

    def set_coeffs_indexes(self, **kwargs):
        # map  coeffs ot it's index
        # like (a,b)-> (params[+0], params[+1])
        map_cti = dict(kwargs['coeffs_to_indexes'])
        self.coeffs_gen.set_coeffs_indexes(map_cti)
    

def cpp(term):
    # gen = CppGen(term)
    return(term.lex[-1])


class CppOutsForTerms():
    '''
    DESCRIPTION:
    If pattern (termDemo) should contain
    cpp out
    then
    there should exist function
    (get_out_for_termDemo)
    and 
    if this function use some
    parameters, they must exist
    and initiated in params before.
    (all that happened in Parser.py)
    '''
    # use varIndexs for all
    # CppOutsForTerms objects
    dataTermVarsSimpleGlobal = {'varIndexs': []}

    def __init__(self, params):
        self.params = params
        
        self.dataTermVarsPoint = []
        self.dataTermVarsPointDelay = []
        self.dataTermVarSimpleLocal = {'delays': [],
                                       'varIndexs': []}
        self.dataTermVarsSimpleIndep = {'delays': [],
                                        'varIndexs': []}

        #!!!self.diffGen = PureDerivGenerator(params)
        self.dataTermOrder = {'indepVar': [],
                              'order': []}
        
        self.dataTermVarsForDelay = {}
        
        self.dataTermMathFuncForDiffSpec = "empty_func"

        self.dataTermRealForPower = {'real': []}

        # for debugging:
        self.dbg = True
        self.dbgInx = 4

    def get_out_for_term(self, termName):
        '''
        DESCRIPTION:
        Find out for term (termDemo) with termName
        (from Patterns.py). For that method with name
        get_out_for_termDemo must exists.

        INPUT:
        termName - name of term like termVarsPoint1D

        Return:
        function replacer \f args: method(self, args)

        Tests:
        >>> f = cpp.get_out_for_term('diff');
        >>> f()
        '''
        methods = self.__class__.__dict__
        for methodName in methods.keys():
            methodTermName = methodName.split('_')[-1]
            if methodTermName == termName:
                return(lambda *args: methods[methodName](self, *args))

    def get_out_for_termPower(self):
        return("pow(arg_val, arg_power)")


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
    res = lex.re.search(l.val_pattern, 'U')
    t.lex = [res.string, res, 'val_pattern']
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
