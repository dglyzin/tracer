from env.equation.data.terms.output.cpp.patterns.base import Base
from env.equation.data.terms.output.cpp.patterns.base import Params

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.default')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Default(Base):
    
    '''node.name.lex[0]
    '''
    
    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'default'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''

        # params = Params()

        value = self.net.get_term_value(node)
        self.params['value'] = value
        # self.params['value'] = node.name.lex[0]
        
        # params['value'] = value
        # self.net.set_output_data(node, self.net.get_params_field_name(),
        #                          params)
        
    def print_out(self):
    
        '''For generate node out'''
        self.params.has_param('value', 'Default')
        return(self.params['value'])
