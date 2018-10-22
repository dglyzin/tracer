from env.equation.data.terms.output.sympy.patterns.base import Base
from env.equation.data.terms.output.sympy.patterns.base import Params
from env.equation.data.terms.common.sympy.base import CommonSympy
from env.equation.data.terms.common.sympy.diff import DiffSympy


import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_sympy.diff')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Diff(Base, CommonSympy, DiffSympy):

    '''Generate cpp data for diff:
    D[U(t-1.1), {x, 3}] -> sympy.diff(U(t-1.1, x), x, 3)'''

    def __init__(self, net):

        Base.__init__(self, net)
        self.id = 'diff'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for dinamicaly fill local data'''
        '''Orders and varList will be set here
        from node's pattern (like {x, 2})
        '''

        params = Params()

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
        params['var'] = self.add_args(var, reg_pattern)

        free_vars = self.get_free_vars(reg_pattern)
        params['free_vars'] = free_vars
        
        out = self.make_diff_pattern(var, free_vars)
        '''
        out = "sympy.diff(%s," % (var)
        for free_var in free_vars:
            order = free_vars[free_var]
            out += "%s, %s" % (free_var, order)
        out += ")"
        '''
        # out = "sympy.diff(%s, %s, %s)" % (var, free_var, order)
        
        params['out'] = out
        self.params['out'] = out

        self.net.set_output_data(node, self.net.get_params_field_name(),
                                 params)
        
    def print_out(self):
        
        '''For generate node out'''
        
        return(self.params['out'])

