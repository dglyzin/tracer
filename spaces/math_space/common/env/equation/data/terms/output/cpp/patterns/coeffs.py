from env.equation.data.terms.output.cpp.patterns.base import Base

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.coeffs')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Coeffs(Base):
    
    '''map  coeffs ot it's index
    like (a,b)-> (params[+0], params[+1])
    '''
    
    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'coeffs'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for fill local data'''

        self.set_coeff_index(node)

    def set_coeff_index(self, node):
        
        coeffs = self.net.get_term_value(node)
        # coeffs = node.name.lex[0]

        self.params.has_param('map_cti', 'Coeffs')

        self.params['coeffsIndex'] = self.params['map_cti'][coeffs]
        
    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''

        self._set_coeffs_indexes(**kwargs)

    def set_coeffs_indexes(self, **kwargs):

        '''
        Input:
        coeffs_to_indexes=[('a', 0), ('b', 1)]
        '''
        try:
            # map  coeffs ot it's index
            # like (a,b)-> (params[+0], params[+1])
            map_cti = dict(kwargs['coeffs_to_indexes'])
            self.params['map_cti'] = map_cti
        except:
            logger.info("kwargs['coeffs_to_indexes'] fail")

    def print_out(self):
        
        '''For generate node out'''

        self.params.has_param('coeffsIndex', 'Coeffs')

        coeffsIndex = self.params['coeffsIndex']
        
        return('params['
               + str(coeffsIndex)
               + ']')

