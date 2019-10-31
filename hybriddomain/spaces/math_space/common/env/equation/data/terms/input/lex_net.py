import abc


class LexNet():
    '''Regexp pattern's for lexical analysis of sent.

    Transform implemented lexem into grammar's terminals.
    
    Input:
    terms_gens - list of term's generators.
                 Each must have __call__ method
                    if supposed to be used in lex tokenizer
                 and .id for name.

    patterns_order - term names (id's) in order they will
                     have been checked in lex tokenizer.
                     More complex term must be close to top.

    map_ptg - map terms id to they grammars terms.

    Examples:

    D[U,{x, 3}]+U -> a+a
    D[U,{x, 3}]+sin(x+y) -> a+fa+a)
    (D[U,{x, 3}]+U)^3+3 -> (a+aw+a

    for grammar's terminals
       a (for D, U, digits, ...),
       +, (, ),
       w (right for ^3),
       f (for functions sin(, cos(, ...)
    '''
    metaclass = abc.ABCMeta

    def __init__(self):

        terms_gens = self.get_terms_gen()
        patterns_order = self.get_patterns_order()
        map_ptg = self.get_map_ptg()

        self.terms = {}

        for gen in terms_gens:
            term = gen(self)
            self.terms[term.id] = term

        self.patterns = []

        # add patterns for searching in lex.
        # order is important:
        for name in patterns_order:
            pattern = self.terms[name]()
            self.patterns.append((name, pattern))

        '''
        self.patterns.append(('diff', self.diff_pattern))
        self.patterns.append(('bdp', self.bound_delay_point))
        self.patterns.append(('func', self.func_pattern))
        self.patterns.append(('diff_time_var_pattern',
                              self.var_diff_t_pattern))
        self.patterns.append(('var_pattern', self.var_pattern))
        self.patterns.append(('free_var_pattern', self.free_var_pattern))
        self.patterns.append(('time_pattern', self.time_pattern))
        self.patterns.append(('coefs_pattern', self.coefs_pattern))
        self.patterns.append(('pow_pattern', self.pow_pattern))
        self.patterns.append(('float_pattern', self.term_float))
        # self.patterns_dict = dict(self.patterns)
        '''

        # map_patterns_to_grammar:
        self.map_ptg = map_ptg

    @abc.abstractmethod
    def get_terms_gen(self):
        raise(BaseException("get_terms_gen must be implemented"))

    @abc.abstractmethod
    def get_patterns_order(self):
        raise(BaseException("get_patterns_order must be implemented"))

    @abc.abstractmethod
    def get_map_ptg(self):
        raise(BaseException("get_map_ptg must be implemented"))
