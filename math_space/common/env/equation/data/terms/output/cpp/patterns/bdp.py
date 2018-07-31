from env.equation.data.terms.output.cpp.patterns.base import Base

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.bdp')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Bdp(Base):

    '''For bound like "V(t-1.1,{x,1.3}{y, 5.3})"'''

    def __init__(self, net):
        Base.__init__(self, net)
        self.id = 'bdp'

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
        self.set_var_index(node)
        
        self.set_varList(node)
        
        # add delays data for postproc:
        if delay_data is not None:
            # node.output.cpp.global_data = data
            self.net.set_output_data(node, 'delay_data', delay_data)

    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''
        '''Set shape,
        vars_to_indexes'''
        
        self.set_shape(**kwargs)
        self.set_vars_indexes(**kwargs)
        self.set_blockNumber(**kwargs)
        self.set_dim(**kwargs)

    def set_shape(self, **kwargs):
        '''
        shape=[3, 3]
        '''
        try:
            self.params['shape'] = kwargs['shape']
        except:
            logger.info("kwargs['shape'] fail")

    def print_out(self):

        '''For generate node out'''

        return(self.var_point())

    def var_point(self):
        '''
        DESCRIPTION:
        For patterns like
        U(t,{x,0.7})
        U(t,{x,0.7}{y,0.3})
        '''
        self.params.has_param('dim', 'Bdp')
        self.params.has_param('indepVarList', 'Bdp')
        self.params.has_param('shape', 'Bdp')

        self.params.has_param('blockNumber', 'Bdp')
        self.params.has_param('unknownVarIndex', 'Bdp')

        if self.params['dim'] == 1:

            print(self.params['indepVarList'])
            val_x = self.params['indepVarOrders']['x']
            x = str(int(float(val_x)*self.params['shape'][0]))

            return(self.var_point_1d(x))
        elif self.params['dim'] == 2:

            self.params.has_param('indepVarOrders', 'Bdp')
            val_x = self.params['indepVarOrders']['x']
            val_y = self.params['indepVarOrders']['y']
            
            x = str(int(float(val_x)*self.params['shape'][0]))
            y = str(int(float(val_y)*self.params['shape'][1]))

            return(self.var_point_2d(x, y))

    def var_point_1d(self, x):
        '''
        DESCRIPTION:
        For patterns like U(t,{x,0.7})
        '''
        blockNumber = self.params['blockNumber']
        varIndex = self.params['unknownVarIndex']
        '''
        return('source[delay]['+str(x)+'*idxX'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE+'
               + str(varIndex)+']')
        '''
        return('source[delay]['+str(x)+''+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE+'
               + str(varIndex)+']')

    def var_point_2d(self, x, y):
        '''
        DESCRIPTION:
        For U(t,{x,0.7}{y,0.3})
        '''
        blockNumber = self.params['blockNumber']
        varIndex = self.params['unknownVarIndex']
        '''
        return(('source[delay][('+str(x)+'*idxX'
                + '+'
                + str(y)+'*idxY*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE+'
                + str(varIndex)+']'))
        '''
        return(('source[delay][('+str(x)+''
                + '+'
                + str(y)+'*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE+'
                + str(varIndex)+']'))

