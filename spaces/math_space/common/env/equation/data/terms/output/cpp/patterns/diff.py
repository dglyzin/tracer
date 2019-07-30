import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
# print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_common import GenPureCommon

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_borders import GenPureBorders

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_ics import GenPureIcs

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_vertexs import GenPureVertexs

from env.equation.data.terms.output.cpp.patterns.base import Base
# from env.equation.data.terms.output.cpp.additions.deriv import PureDerivGenerator
from env.equation.data.terms.output.cpp.additions.deriv_old import MixDerivGenerator

import logging
# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('replacer_cpp.diff')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('diff.py')
logger.setLevel(level=log_level)


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
        self.params.has_param('indepVarOrders', 'Diff')
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
            if self.params['diffMethod'] == 'borders':
                return(self.diff_pure_borders())
            if self.params['diffMethod'] == 'interconnect':
                return(self.diff_pure_ics())
            if self.params['diffMethod'] == 'vertex':
                return(self.diff_pure_vertex())

    def diff_pure_common(self):
        # for debug
        logger.debug("diffType: pure, common")

        blockNumber = self.params["blockNumber"]
        unknownVarIndex = self.params["unknownVarIndex"]
        indepVar = self.params["indepVarList"][0]
        indepVarOrders = self.params["indepVarOrders"]
        logger.debug("indepVarOrders:")
        logger.debug(indepVarOrders)
        gen = GenPureCommon(blockNumber, unknownVarIndex,
                            indepVar, indepVarOrders)
        out = gen.common_diff()

        return(out)

    def diff_pure_borders(self):
        # for debug
        logger.debug("diffType: pure, spec")

        blockNumber = self.params["blockNumber"]
        unknownVarIndex = self.params["unknownVarIndex"]
        indepVar = self.params["indepVarList"][0]
        indepVarOrders = self.params["indepVarOrders"]

        side = self.params['side']
        border_func = self.params['func']
    
        gen = GenPureBorders(blockNumber, unknownVarIndex,
                             indepVar, indepVarOrders)
        gen.set_special_params(side)
        out = gen.borders_diff(border_func)

        logger.debug("\ndiff_pure_borders out:")
        logger.debug(out)
        logger.debug("\nparams:")
        logger.debug(self.params)

        return(out)

    def diff_pure_ics(self):

        # for debug
        logger.debug("diffType: pure, interconnect")

        blockNumber = self.params["blockNumber"]
        unknownVarIndex = self.params["unknownVarIndex"]
        indepVar = self.params["indepVarList"][0]
        indepVarOrders = self.params["indepVarOrders"]

        side = self.params['side']
        firstIndex = self.params['firstIndex']
        secondIndexSTR = self.params['secondIndexSTR']

        gen = GenPureIcs(blockNumber, unknownVarIndex,
                         indepVar, indepVarOrders)
        gen.set_special_params(side, firstIndex, secondIndexSTR)
        out = gen.ics_diff()
        return(out)

    def diff_pure_vertex(self):

        # for debug
        logger.debug("diffType: pure, vertexs")

        blockNumber = self.params["blockNumber"]
        unknownVarIndex = self.params["unknownVarIndex"]
        indepVar = self.params["indepVarList"][0]
        indepVarOrders = self.params["indepVarOrders"]

        border_func = self.params['func']
        vertex_sides = self.params['vertex_sides']

        gen = GenPureVertexs(blockNumber, unknownVarIndex,
                             indepVar, indepVarOrders)
        gen.set_special_params(vertex_sides)

        out = gen.vertexs_diff(border_func)

        logger.debug("\ndiff_pure_vertex out:")
        logger.debug(out)
        logger.debug("\nparams:")
        logger.debug(self.params)

        return(out)

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
        raise(BaseException("\ndiff_none is depricated"
                            + "\nset diffMethod first"))

