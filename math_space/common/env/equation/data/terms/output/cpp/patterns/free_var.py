from env.equation.data.terms.output.cpp.patterns.base import Base

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.free_var')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class FreeVar(Base):

    '''x->idxX, y->idxY, z->idxZ '''

    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'free_var'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for fill local data.
        Extract var_name'''

        self.params['var_name'] = self.net.get_term_value(node)
        # self.params['var_name'] = node.name.lex[0]

    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''
        pass

    def print_out(self):

        '''x->idxX, y->idxY, z->idxZ '''

        self.params.has_param('var_name', 'FreeVar')
        var_name = self.params['var_name']
        return("idx"+var_name.upper())


