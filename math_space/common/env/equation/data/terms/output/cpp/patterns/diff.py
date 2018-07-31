from env.equation.data.terms.output.cpp.patterns.base import Base
from env.equation.data.terms.output.cpp.additions.deriv import PureDerivGenerator
from env.equation.data.terms.output.cpp.additions.deriv import MixDerivGenerator

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_cpp.diff')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class Diff(Base):

    '''Generate cpp data for diff:
    D[U(t-1.1), {x, 3}]'''

    def __init__(self, net):

        Base.__init__(self, net)
        self.id = 'diff'

    def set_node_data(self, **kwargs):

        '''For setting data before replacment'''
        
        self.set_diff_type(**kwargs)
        self.set_vars_indexes(**kwargs)
        self.set_blockNumber(**kwargs)

    def set_diff_type(self, **kwargs):
        '''
        Inputs:
           diffType="pure", diffMethod="common"

           diffType="pure", diffMethod="special",
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
        if diffMethod == 'special':
            try:
                self.params['side'] = kwargs['side']
                self.params['func'] = kwargs['func']
            except:
                raise(BaseException(('for method special side'
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
            except:
                raise(BaseException(('for method vertex vertex_sides'
                                     + "(see Diff._set_diff_type for more)"
                                     + 'must be given')))
    
    def get_node_data(self, node):

        '''For getting data from node during replacment'''
        '''Some data will be used by generator, some added to
        node directly'''
        '''Used for dinamicaly fill local data'''
        '''Orders and varList will be set here
        from node's pattern (like {x, 2})
        Return delay data.
        '''

        self.set_varList(node)
        self.set_var_index(node)
        delay_data = self.set_delay(node)

        # add delays data for postproc:
        if delay_data is not None:
            # node.output.cpp.global_data = data
            self.net.set_output_data(node, 'delay_data', delay_data)

        '''
        if delay_data is not None:
            return({'delay_data': delay_data})
        else:
            return(None)
        '''

    def print_out(self):
        
        '''For generate node out'''
        '''
        global_params = {
            # int: shift index for variable like
            # like (U,V)-> (source[+0], source[+1])
            'unknownVarIndex': 0
                
            'blockNumber': 0
            'side': 0

            'diffType': 'pure'
            'diffMethod': 'vertex'}
        '''
        # check params avelable:
        self.params.has_param('blockNumber', 'Diff')
        self.params.has_param('unknownVarIndex', 'Diff')
        self.params.has_param('indepVarList', 'Diff')
        self.params.has_param('diffMethod', 'Diff')
        return(self.diff())

    def diff(self):
        '''
        DESCRIPTION:
        self.params should be initiated first.
        '''
        logger.debug("FROM diff:")
        if (self.params['diffMethod'] is None
            or self.params['diffType'] is None):
            raise(BaseException('set_diff_type first'))
        if self.params['diffType'] == 'pure':
            if self.params['diffMethod'] == 'common':
                return(self.diff_pure_common())
            if self.params['diffMethod'] == 'special':
                return(self.diff_pure_spec())
            if self.params['diffMethod'] == 'interconnect':
                return(self.diff_pure_ics())
            if self.params['diffMethod'] == 'vertex':
                return(self.diff_pure_vertex())

    def diff_pure_common(self):
        # for debug
        logger.debug("diffType: pure, common")
        diffGen = PureDerivGenerator(self.params)
        out = diffGen.common_diff()
        return(out)

    def diff_pure_spec(self):
        # for debug
        logger.debug("diffType: pure, spec")
        diffGen = PureDerivGenerator(self.params)
        func = self.params['func']
        out = diffGen.special_diff(func)
        return(out)

    def diff_pure_ics(self):
        # for debug
        logger.debug("diffType: pure, interconnect")
        diffGen = PureDerivGenerator(self.params)
        out = diffGen.interconnect_diff()
        return(out)

    def diff_pure_vertex(self):
        logger.debug("vertex not implemented")
        return(None)

    def diff_mix_common(self):
        # for debug
        logger.debug("diffType: pure, common")
        diffGen = MixDerivGenerator(self.params)
        out = diffGen.common_diff()
        return(out)

    def diff_mix_spec(self):
        # for debug
        logger.debug("diffType: pure, spec")
        diffGen = MixDerivGenerator(self.params)
        func = self.params['func']
        out = diffGen.special_diff(func)
        return(out)

    def diff_mix_ics(self):
        # for debug
        logger.debug("diffType: pure, interconnect")
        diffGen = MixDerivGenerator(self.params)
        out = diffGen.interconnect_diff()
        return(out)

    def diff_none(self):
        # for debug
        logger.debug("diffMethod: None")
        diffGen = PureDerivGenerator(self.params)
        func = self.params['func']
        out = diffGen.diff(func)
        return(out)
