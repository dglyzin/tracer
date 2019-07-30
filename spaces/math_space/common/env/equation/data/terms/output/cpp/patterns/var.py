from env.equation.data.terms.output.cpp.patterns.base import Base

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.var')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Var(Base):

    '''For U, V, U(t-1.1)'''

    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'var'

    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for fill local data'''
        '''Orders and varList will be set here
        from node's pattern (like {x, 2})
        Return delay data
        '''

        delay_data = self.set_delay(node)

        # add delays data for postproc:
        if delay_data is not None:
            # node.output.cpp.global_data = data
            self.net.set_output_data(node, 'delay_data', delay_data)

        self.set_var_index(node)

    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''
        '''int: shift index for variable like
        like (U,V)-> (source[+0], source[+1])
        '''
        '''
        Input:
        vars_to_indexes=[('U', 0), ('V', 1)]
        '''
                
        self.set_vars_indexes(**kwargs)

    def print_out(self):
        
        '''For generate node out'''

        self.params.has_param('unknownVarIndex', 'Var')

        return(self.var_simple())

    def var_simple(self):
        '''
        DESCRIPTION:
        varIndex usage:
        source[][idx+0] - x
        source[][idx+1] - y
        source[][idx+2] - z
        
        '''

        varIndex = self.params['unknownVarIndex']
        return('source['
               + 'delay'
               + '][idx + '
               + str(varIndex)
               + ']')

    def var_1d(self):
        # TODO
        self.params.has_param('blockNumber', 'Var')

        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return('source[delay][idx'+'+'+'idxX'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE'
               + '+'+str(varIndex)+']')
        
    def var_2d(self):
        # TODO
        self.params.has_param('blockNumber', 'Var')

        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return(('source[delay][(idx'
                + '+'
                + 'idxX'+'*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE'
                + '+'+str(varIndex) + ']'))
