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
        out = self.print_out()
        self.net.set_output_out(node, out)
        # node.output.cpp.out = self.print_out()

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

    def set_blockNumber(self, **kwargs):
        try:
            blockNumber = kwargs['blockNumber']
            self.params['blockNumber'] = blockNumber
        except KeyError:
            logger.info("kwargs['blockNumber'] fail")

    def set_var_index(self, node):
        var = self.net.get_term_pattern(node).group('val')
        # var = node.name.lex[1].group('val')

        # for case like U(t-1.1)
        var = var[0]
        self.params['unknownVarIndex'] = self.params['map_vti'][var]

    def set_vars_indexes(self, **kwargs):
        '''Input:

        - ``unknownVarIndex`` -- shift index for variable
        (like (U, V)-> (source[+0], source[+1]))
        (Ex: [('U', 0), ('V', 1)])
        '''

        try:
            map_vti = dict(kwargs['vars_to_indexes'])
            self.params['map_vti'] = map_vti
        except KeyError:
            logger.info("kwargs['vars_to_indexes'] fail")

    def set_delay(self, node):

        '''Find values and it's delay (like (t-1.1))
        and add node index to global_params
        (for conversion in postprocessing)'''

        pattern = self.net.get_term_pattern(node)
        # pattern = node.name.lex[1]
        # print(pattern.groups())
        delay = pattern.group('delay')
        if delay is not None:
            self.net.global_params.delays_owner_id += 1
            delay_index = self.net.global_params.delays_owner_id
            self.net.global_params.delays[delay_index] = delay

            # var_index ex: U(t-1.1)
            var_index = pattern.group('val')
            return((delay_index, var_index, delay))
            
        return(None)

    def set_varList(self, node):

        '''Find values and it's orders (like {x, 2})
        Or {x, 2.1} for case of bdp'''
        
        pattern = self.net.get_term_pattern(node)
        # pattern = node.name.lex[1]

        logger.debug("pattern.string:")
        logger.debug(pattern.string)
        logger.debug("pattern.groupdict():")
        logger.debug(pattern.groupdict())

        for var in 'xyz':
            order = pattern.group('val_'+var)
            if order is not None:
                self.params['indepVarList'] = [var]
                '''
                if 'indepVarList' in self.params:
                    self.params['indepVarList'].append(var)
                else:
                    self.params['indepVarList'] = [var]
                '''
                # do not refill orders if they alredy exist:
                if 'indepVarOrders' in self.params:
                    self.params['indepVarOrders'][var] = float(order)
                else:
                    self.params['indepVarOrders'] = dict([(var, float(order))])
                # break
                
    def set_diff_type(self, **kwargs):
        '''
        Inputs:
           diffType="pure", diffMethod="common"

           diffType="pure", diffMethod="borders",
           side=0, func="sin(x)"

           diffType="pure", diffMethod="interconnect",
           side=0, firstIndex=0, secondIndexSTR=1
        '''

        try:
            self.params['diffType'] = kwargs['diffType']
            self.params['diffMethod'] = kwargs['diffMethod']
        except:
            raise(BaseException("for diff term diffType and diffMethod"
                                + "(see Diff._set_diff_type for more)"
                                + " params needed"))

        diffMethod = self.params['diffMethod']
        if diffMethod == 'borders':
            try:
                self.params['side'] = kwargs['side']
                self.params['func'] = kwargs['func']
            except:
                raise(BaseException(('for method borders side'
                                     + ' and func must be given'
                                     + "(see Diff._set_diff_type for more)")))
        elif diffMethod == 'interconnect':
            try:
                self.params['side'] = kwargs['side']
                self.params['firstIndex'] = kwargs['firstIndex']
                self.params['secondIndexSTR'] = kwargs['secondIndexSTR']
            except:
                raise(BaseException(('for method interconnect'
                                     + ' side, firstIndex and secondIndexSTR'
                                     + ' must be given'
                                     + "(see Diff._set_diff_type for more)")))
        elif diffMethod == 'vertex':
            try:
                self.params['vertex_sides'] = kwargs['vertex_sides']
                self.params['func'] = kwargs['func']
            except:
                raise(BaseException(('for method vertex vertex_sides'
                                     + "(see Diff._set_diff_type for more)"
                                     + 'must be given')))

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')
