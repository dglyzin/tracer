from env.equation.data.terms.output.sympy.patterns.base import Params

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.func')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Idx():
    
    '''for f (left=f right=))'''
    
    def __init__(self, net):
        self.net = net
        self.gnet = self.net.net

        self.params = Params()

        # this meen left_term.name == 'i'
        # right_node.name == ')'
        self.id = 'l:i|r:]'

    def __call__(self, node_br):
        
        '''Add cpp out to brackets'''

        successors = self.gnet.get_successors(node_br)
        
        left_node = successors[0]
        right_node = successors[-1]

        args_node = successors[1]
        
        # get node data:
        self.get_node_data(left_node, right_node)
        
        # transform to cpp:
        left_out, right_out = self.print_out()

        self.gnet.set_output_out(left_node, left_out)
        self.gnet.set_output_out(right_node, right_out)

    def get_node_data(self, left_node, right_node):

        '''Used for fill local data'''

        params = Params()
        
        # FOR left_node (a[):
        if 'variable' in left_node.args:
            # for func like f, g, h value must exist
            # substituted with subs:
            value = str(left_node.args['variable']['value'])+"["
        else:
            # for func like sin, cos, exp:
            # func = left_node.name.lex[0][:-1]
            value = self.gnet.get_term_value(left_node)[:-1]
        # END FOR

        params['value'] = value
        self.params['value'] = value
        self.gnet.set_output_data(left_node, self.gnet.get_params_field_name(),
                                  params)

    def print_out(self):
        
        func = self.params['value']
        # transform to sympy:
        self.params['out'] = "%s" % (func)

        right = "]"
        return(self.params['out'], right)
