'''This is how complex terms can be implemented.
This is not good solution beter if diff term implemented
as bracket. In that case One don't need to have access to
global data (self and node parameters in make_diff) and
just replace D -> diff. 
In current implemenation it is not possible to subs something
instead of alredy given (D[U] subs U)
DEPRICATED'''

from env.equation.data.terms.slambda.sympy.patterns.ids.diff import Diff
from env.equation.data.terms.slambda.sympy.patterns.ids.diff_time_var import DiffTimeVar
from env.equation.data.terms.slambda.sympy.patterns.ids.dot import DotTranspose


def make_diff(self, node, sympy):
    gen = Diff(self)
    slambda = gen.get_lambda(node)
    return(lambda: slambda(sympy))


def make_diff_time(self, node, sympy):
    gen = DiffTimeVar(self)
    slambda = gen.get_lambda(node)
    return(lambda: slambda(sympy))


def make_dot(self, node, sympy):
    gen = DotTranspose(self)
    slambda = gen.get_lambda(node)
    if slambda is not None:
        return(slambda)
    else:
        value = self.get_term_value(node)
        raise(BaseException("slambda for dot %s is not supported" % (value)))
 

terms_gens_id = dict([('diff', make_diff),
                      ('diff_time', make_diff_time),
                      ('dot', make_dot)])
