from tests import tests
import re
from functools import reduce


def preproc(sent):
    sent = sent.replace(" ", "")


class Lex():
    def __init__(self):

        self.patterns = {}

        self.init_terms()
        self.init_base_patterns()
        self.init_var_pattern()
        self.init_bound_pattern()
        self.init_diff_pattern()

    def init_terms(self):
        self.dep_vars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        self.indep_vars = 'xyz'
        self.time_var = 't'

        params = self.dep_vars.lower()
        params = params.replace(self.time_var, "")
        for a in self.indep_vars:
            params = params.replace(a, "")
        self.params = params

        func = ['exp', 'sqrt', 'log',
                'sin', 'cos', 'tan',
                'sinh', 'tanh']
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
        self.arg_time = r"[t]-%s" % (self.term_delay)

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
        val_pattern = ('[%s](\(%s\))?'
                       % (self.dep_vars, self.arg_time))
        
        self.patterns['val_pattern'] = val_pattern

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
        self.patterns['bdp'] = bound_delay_point

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
        diff_pattern = ('D\[[%s](\(%s\))?,%s\]'
                        % (self.dep_vars, self.arg_time, self.args_ord))
        
        self.diff_pattern = diff_pattern
        self.patterns['diff_pattern'] = diff_pattern


def lex(sent="a+U*U*V+D[V,{y,1}]-c*D[U,{x,2}]", out=None):

    '''Return dict with:
    D[pattern_matched_term] = [pattern_name, match_object, index]
    where index is count of such pattern in sent (from zero)'''

    g = Lex()

    # if first time:
    if out is None:
        out = {"out_str": sent}

    # check all patterns:
    for pattern in g.patterns:
        res = re.search(g.patterns[pattern], out["out_str"])
        if res is not None:
            # first is found element (implementation of pattern),
            # rest is str with it replaced by it's term (pattern):
            first = res.group()
            rest = out["out_str"].replace(first, pattern)

            out["out_str"] = rest

            # save pattern type and it's number:
            if pattern in out.keys():
                out[pattern] += 1
                out[first] = [pattern, res, out[pattern]]
            else:
                out[pattern] = 0
                out[first] = [pattern, res, 0]
            
            # go next
            return(lex(sent, out))

    # if no pattern found return result:
    return(out)


def syn(sent="(exp_1+exp_2)*exp_3"):

    patterns = {}
    patterns['term'] = r'([a-z]|\d.\d|\d|_)*?'
    patterns['term_first'] = r'^' + term
    patterns['term_plus_term'] = term_first + r'\+'
    patterns['term_mult_term'] = term_first + r'\*'
    patterns['term_bracket'] = "(" + term

    res = None

    for pattern in patterns:
        res = re.search(pattern, sent)
        first = res.group()
        rest = sent[res.end():]
        
        if pattern == 'term_bracket':
            pass


def parse(sent=r"U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]"):
    try:
        ''' For term "V(t-1.5,{x,1.3})" '''

        res = re.search(bound_delay_point,
                        sent)
    except:
        print("exception")
