from env.equation.data.terms.output.cpp.patterns.base import Base

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.float')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Float(Base):
    
    '''1.1
    '''
    
    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'float'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''

        self.value = self.net.get_term_value(node)
        # self.value = node.name.lex[0]

    def print_out(self):
    
        '''For generate node out'''

        return(self.value)
