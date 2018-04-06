'''
! input sent must not have spaces.
 
Examples:

>>> import lex
>>> goal = lex.lex('D[U,{x, 3}]+sin(x+y)');goal
['a', '+', 'f', 'x', '+', 'y', ')']

>>> goal[0].lex
['D[U,{x,3}]', <_sre.SRE_Match object; span=(0, 10), match='D[U,{x,3}]'>]

'''
import re
from functools import reduce
from tokenizer.words import Word


def preproc(sent):
    sent = sent.replace(" ", "")


class Lex():
    '''Regexp pattern's for lexical analysis of sent.

    Transform implemented lexem into grammar's terminals.
    
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
    def __init__(self):

        self.init_terms()
        self.init_base_patterns()
        self.init_var_pattern()
        self.init_coefs_pattern()
        self.init_bound_pattern()
        self.init_diff_pattern()
        self.init_pow_pattern()
        self.init_func_pattern()
        self.init_free_var_pattern()

        self.patterns = []
        
        # order is important
        self.patterns.append(('diff_pattern', self.diff_pattern))
        self.patterns.append(('bdp', self.bound_delay_point))
        self.patterns.append(('func_pattern', self.func_pattern))
        self.patterns.append(('var_pattern', self.var_pattern))
        self.patterns.append(('free_var_pattern', self.free_var_pattern))
        self.patterns.append(('coefs_pattern', self.coefs_pattern))
        self.patterns.append(('pow_pattern', self.pow_pattern))
        self.patterns.append(('float_pattern', self.term_float))
        self.patterns_dict = dict(self.patterns)

        # map_patterns_to_grammar:
        self.map_ptg = dict([('diff_pattern', 'a'),
                             ('bdp', 'a'),
                             ('var_pattern', 'a'),
                             ('free_var_pattern', 'a'),
                             ('coefs_pattern', 'a'),
                             ('pow_pattern', 'w'),
                             ('func_pattern', 'f'),
                             ('float_pattern', 'a')])

    def init_terms(self):
        self.dep_vars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.coefs = self.dep_vars.lower()[:-3]
        self.indep_vars = 'xyz'
        self.time_var = 't'

        params = self.dep_vars.lower()
        params = params.replace(self.time_var, "")
        for a in self.indep_vars:
            params = params.replace(a, "")
        self.params = params

        func = ['exp', 'sqrt', 'log',
                'sin', 'cos', 'tan',
                'sinh', 'tanh', 'f', 'g', 'h']
        self.func = func

        self.unary = ['-']
        self.binary = ['+', '-', '*', '/']

    def init_base_patterns(self):

        self.term_int = r"\d"

        # 1.5 or 1:
        self.term_float = r"\d\.\d|\d"

        # (?P<delay>1.5)
        self.term_delay = r"(?P<delay>%s)" % (self.term_float)

        #  find patterns like t-1.5:
        # self.arg_time = r"[t]-%s" % (self.term_delay)
        self.arg_time = r"[t](-%s)?" % (self.term_delay)

    def _make_args(self, term_type):

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

    def init_var_pattern(self):

        '''For U or U(t-1.5)'''

        var_pattern = ('(?P<val>[%s](\(%s\))?)'
                       % (self.dep_vars, self.arg_time))
        self.var_pattern = var_pattern

    def init_free_var_pattern(self):

        '''For x, y, z'''

        var_pattern = "[%s]" % (self.indep_vars)
        self.free_var_pattern = var_pattern

    def init_coefs_pattern(self):
        coefs_pattern = ('[%s]'
                         % (self.coefs))
        self.coefs_pattern = coefs_pattern

    def init_bound_pattern(self):

        ''' For "V(t-1.1,{x,1.3})" in begining of sent'''

        self.args_space = self._make_args(self.term_float)

        # find V(t-1.1,{x,1.3}) in begining of sent:
        # >>> re.search(bound_delay_point, "V(t-1.1,{x,1.3})").group()
        # 'V(t-1.1,{x,1.3})'
        #bound_delay_point = (r"^[%s]\(%s,%s\)"
        #                     % (self.dep_vars, self.arg_time, self.args_space))
        bound_delay_point = (r"[%s]\(%s,%s\)"
                             % (self.dep_vars, self.arg_time, self.args_space))
        
        self.bound_delay_point = bound_delay_point
        
    def init_diff_pattern(self):

        ''' For
        D[U(t-5.1),{y,2}]
        D[U,{x,1}]
        in begining of sent.
        '''

        self.args_ord = self._make_args(self.term_int)

        # for D[U,{x,2}] or D[U(t-1.1),{x,1}{y,3}]
        # In [96]: re.search(g.diff_pattern,"D[U(t-1),{x,1}{y,3}]").groupdict()
        # Out[96]: {'delay': '1', 'val_x': '1', 'val_y': '3', 'val_z': None}
        #diff_pattern = ('^D\[[%s](\(%s\))?,%s\]'
        #                % (self.dep_vars, self.arg_time, self.args_ord))
        # diff_pattern = ('D\[[%s](\(%s\))?,%s\]'
        #                % (self.dep_vars, self.arg_time, self.args_ord))
        diff_pattern = ('D\[%s,%s\]'
                        % (self.var_pattern, self.args_ord))
        self.diff_pattern = diff_pattern

    def init_pow_pattern(self):
        
        '''For (a)^3'''
        
        pow_pattern = (r'\)\^\d')
        self.pow_pattern = pow_pattern

    def init_func_pattern(self):
        
        '''For sin(a)'''

        func = reduce(lambda acc, f: f + '|' + acc, self.func, "")[:-1]
        func_pattern = (r'(%s)\(' % (func))
        self.func_pattern = func_pattern


def split(sent, re_search_out):

    '''Split but only one occurrence'''

    start_index = re_search_out.start()
    end_index = re_search_out.end()
    return([sent[:start_index], sent[end_index:]])


def lex(sent="a+U*U*V+D[V,{y,1}]-c*D[U,{x,2}]"):

    ''' Lexical analysis of sent.

    lex sent =
      case find_pattern(sent, patterns) of
           [left, pattern, right] -> lex(left)+Word(pattern)+lex(right)
           [left, pattern] -> lex(left)+Word(pattern)
           [pattern, right] -> Word(pattern)+lex(right)
           otherwise -> list(sent)
      where
            -- return list of remained words:
            find_pattern sent [] = [Word(char) for char in sent]
            
            -- return res or try with others patterns:
            find_pattern sent [x:xs] = if res=re.find(x, sent) then res
                                          else find_pattern sent xs

    Input: string without spaces.

    Return: list[elms] where elems is Word
            if pattern found then elms.lex = ['found lexem', re.match object]
            else then elms.lex = [elms.name] where name is original char.
    Tests:
    >>> t = lex("a+U*U*V+D[V,{y,1}]-c*D[U,{x,2}]");t
    ['a', '+', 'a', '*', 'a', '*', 'a', '+', 'a', '-', 'a', '*', 'a']
    >>> type(t[0])
    Word
    >>> t[8].lex[1].group()
    'D[V,{y,1}]'
    '''
    
    lps = Lex()

    # check all patterns:
    for pattern_name, pattern_value in lps.patterns:
        res = re.search(pattern_value, sent)

        if res is not None:
            # recursively transform all word's:

            # first is found element (implementation of pattern),
            # rest is, splited with first, sent:
            first = res.group()
            rest = split(sent, res)

            if len(rest) == 2:
                left = lex(rest[0])
                X = [Word(lps.map_ptg[pattern_name],
                          [first, res, pattern_name])]
                right = lex(rest[1])

                # [left, X, right]
                return(left + X + right)

            elif(len(rest) == 1):
                if res.start == 0:
                    X = [Word(lps.map_ptg[pattern_name],
                              [first, res, pattern_name])]
                    right = lex(rest[0])

                    # [X, right]
                    return(X + right)
                else:
                    left = lex(rest[0])
                    X = [Word(lps.map_ptg(pattern_name),
                              [first, res, pattern_name])]

                    # [left, X]
                    return(left + X)
    # if no pattern found split remained:
    # return(list(sent))
    return([Word(char, [char, None, None]) for char in sent])
