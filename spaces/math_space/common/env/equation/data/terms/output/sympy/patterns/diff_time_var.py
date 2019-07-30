from env.equation.data.terms.output.sympy.patterns.base import Base
from env.equation.data.terms.output.sympy.patterns.base import Params
from env.equation.data.terms.common.sympy.base import CommonSympy

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_sympy.diff_time')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class DiffTimeVar(Base, CommonSympy):

    '''Generate cpp data for diff:
    D[U(t-1.1), {x, 3}] -> sympy.diff(U(t-1.1, x), x, 3)'''

    def __init__(self, net):

        Base.__init__(self, net)
        self.id = 'diff_time'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for dinamicaly fill local data'''
        '''Orders and varList will be set here
        from node's pattern (like {x, 2})
        Return delay data.
        '''
        params = Params()

        reg_pattern = self.net.get_term_pattern(node)

        # diff var (U):
        var = reg_pattern.group('val')

        # add args x, y to var:
        var = self.add_args(var, reg_pattern)

        # transform to sympy:
        out = "sympy.diff(%s, t)" % (var)

        params['out'] = out
        self.params['out'] = out

        self.net.set_output_data(node, self.net.get_params_field_name(),
                                 params)
        
    def print_out(self):
        
        '''For generate node out'''
        
        return(self.params['out'])

