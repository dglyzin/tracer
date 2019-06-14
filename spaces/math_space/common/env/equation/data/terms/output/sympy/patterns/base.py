
import abc

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.base')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Params(dict):
    '''
    def __init__(self):
        self.diffType = None  # 'pure'
        self.diffMethod = None  # 'vertex'

        # int: shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndexes = []

        # {x, 2}
        self.indepVarList = []
        self.indepVarOrders = {}
        self.derivOrder = None

        self.blockNumber = None
        self.side = None
    '''

    def has_param(self, key, source):
        try:
            self[key]
        except KeyError:
            raise(KeyError('for term %s dont have %s param' % (source, key)))
            

class Base():
    metaclass = abc.ABCMeta

    '''Common methods for all cpp terms'''

    def __init__(self, net):

        self.net = net
        self.params = Params()

    def __call__(self, node):

        '''Extract data from node lex pattern add it
        to node.cpp.global_data and generate out to it
        node.output.cpp.out'''

        self.get_node_data(node)
        
        # transform to cpp:
        self.net.set_output_out(node, self.print_out())

    @abc.abstractmethod
    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''

        raise(BaseException(('get_node_data method of BaseTerm class'
                             + ' must be implemented')))
    
    @abc.abstractmethod
    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''

        raise(BaseException(('set_node_data method of BaseTerm class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def print_out(self):

        '''For generate node out'''

        raise(BaseException(('print_out method of BaseTerm class'
                             + ' must be implemented')))

    def set_dim(self, **kwargs):
        try:
            dim = kwargs['dim']
            self.params['dim'] = dim
        except KeyError:
            logger.info("kwargs['dim'] fail")

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')
