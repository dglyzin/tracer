from env.equation.data.terms.common.sympy.base import CommonSympy
from env.equation.data.terms.common.sympy.diff import DiffSympy


class DiffTimeVar(CommonSympy, DiffSympy):

    '''Generate cpp data for diff:
    D[U(t-1.1), {x, 3}] -> sympy.diff(U(t-1.1, x), x, 3)'''

    def __init__(self, net):
        self.net = net
        self.id = 'diff'

    def get_lambda(self, node):
    
        reg_pattern = self.net.get_term_pattern(node)

        # diff var (U):
        var = reg_pattern.group('val')

        '''
        # find diff orders (free_var: x, order: 1):
        for free_var in 'xyz':
            order = reg_pattern.group('val_'+free_var)
            if order is not None:
                break
        '''

        # add args x, y to var:
        var = self.add_args(var, reg_pattern)
        # free_vars = self.get_free_vars(reg_pattern)
        diff = self.make_diff_pattern(var, {'t': 1})
        out = lambda sympy: sympy.sympify(diff)
        # print("from lambda diff")
        print(diff)
        return(out)
        # out = "sympy.diff(%s, %s, %s)" % (var, free_var, order)
