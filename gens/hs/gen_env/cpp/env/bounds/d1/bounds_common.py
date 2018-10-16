from gens.hs.gen_env.cpp.env.base.base_common import GenBaseCommon
from gens.hs.gen_env.cpp.env.bounds.common.bounds_common_cpp import GenCppCommon

from math_space.common.someClasses import Params
from math_space.common.someFuncs import determineNameOfBoundary

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('bounds.bounds_common')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_dom')
logger.setLevel(level=log_level)
'''


class GenCommon(GenBaseCommon, GenCppCommon):
    '''
    # side: <0 -----side 2------ 1>
    '''
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_bounds(self, model, funcNamesStack,
                              ics=[]):
        '''
        DESCRIPTION:

        Collect bounds params for cpp template and dom files
        for all 2d blocks:

        - ``self.net.params.bounds`` -- all bounds
        - ``self.net.params.bounds_edges`` -- bounds
        for edges.

        ics used for checking if interconnect for
        this side exist. So this function must be used
        after set_params_for_dom_interconnects.

        Also add ``bound.funcName`` to ``funcNameStack``
        '''
        # self.params = []
        self.net.params = Params()
        self.net.params.bounds = Params()
        self.net.params.bounds_edges = Params()

        params = [self.make_bound_param(model, block.vertexs[vertex_num])
                  for block in model.blocks
                  for vertex_num in block.vertexs
                  if not self.check_ic_exist((block.vertexs[vertex_num]
                                              .sides_nums[0]),
                                             block.blockNumber, ics)]
        self.net.params.bounds.extend(params)
        self.net.params.bounds_edges.extend(params)

        logger.debug("bounds params:")
        logger.debug(params)
        
        '''
        # for blockNumber, block in enumerate(model.blocks):
        for block in model.blocks:

            blockNumber = block.blockNumber

            # sides_nums = [0, 1]
            # for side_num in [0, 1]:
            for vertex_num in block.vertexs:
                vertex = block.vertexs[vertex_num]

                # for 1d there is only one side:
                side_num = vertex.sides_nums[0]
                # side = block.sides[2]
                if self.check_ic_exist(side_num, blockNumber, ics):
                    continue

                bParams = self.make_bounds(model, vertex)
                self.net.params.append(bParams)
        '''

        # FOR FuncArray
        funcNamesStackLocal = [bound.funcName
                               for bound in self.net.params.bounds]

        logger.debug("funcNamesStackLocal:")
        logger.debug(funcNamesStackLocal)

        self.fill_func_names_stack(funcNamesStack, funcNamesStackLocal)
        # END FOR

    def make_bound_param(self, model, vertex):

        '''Fill this parameters for block bound border
        (vertex in case of 1d)::

        Collect this parameters for template:

             - ``bParams.dim``
             - ``bParams.values`` -- border_values
             - ``bParams.btype``
             - ``bParams.side_num``
             - ``bParams.boundNumber``
             - ``bParams.equationNumber``
             - ``bParams.equation`` -- system of equations
             - ``bParams.funcName``
             - ``bParams.block``
             - ``bParams.blockNumber``
             - ``bParams.boundName`` -- for comment
             - ``bParams.parsedValues``
             - ``bParams.original`` -- for comment

        This parameters also collected for dom:
    
             - ``bound.side``
             - ``bound.blockNumber``
             - ``bParams.funcName``
        '''
        block = vertex.block
        blockNumber = vertex.block.blockNumber

        # for 1d there is only one side:
        side_num = vertex.sides_nums[0]

        # find equation number for side or use default
        equationNum = vertex.equationNumber
        '''
        regsEqNums = [eqReg.equationNumber
                      for eqReg in block.equationRegions
                      if self.test(block, eqReg, side_num)]
        equationNum = (regsEqNums[0] if len(regsEqNums) > 0
                       else block.defaultEquation)
        '''
        eSystem = model.equations[equationNum].copy()

        # find bound region for side or use default
        boundNumber = vertex.boundNumber
        '''
        regionsForSide = [bRegion
                          for k in block.boundRegions
                          for bRegion in block.boundRegions[k]
                          if bRegion.side_num == side_num]
        '''

        # if exist special region for that side
        # if len(regionsForSide) > 0:
        if boundNumber is not None:
            # region = block.boundsRegions[boundNumber]
            # region = regionsForSide[0]
            # boundNumber = region.boundNumber

            bound = model.bounds[boundNumber]

            args = (model, blockNumber, side_num,
                    boundNumber, equationNum)

            # for Dirichlet bound
            if bound.btype == 0:
                func = self.get_func_for_dirichlet(*args)

            # for Neumann bound
            elif bound.btype == 1:
                func = self.get_func_for_neumann(*args)

            funcName = func[0]
            border_values = list(func[1])
            btype = bound.btype
        else:
            # if not, use default

            args = (eSystem, blockNumber, side_num,
                    equationNum)
            func = self.get_func_default(*args)

            funcName = func[0]
            border_values = func[1]
            btype = 1
            boundNumber = -1

        args = (eSystem, model, blockNumber, btype,
                side_num, border_values)
        parsed = self.parse_equations(*args)

        # FOR collect template data:
        bParams = Params()
        bParams.dim = model.dimension
        bParams.values = border_values
        bParams.btype = btype
        bParams.side_num = side_num
        bParams.boundNumber = boundNumber
        bParams.equationNumber = equationNum
        bParams.equation = eSystem
        bParams.funcName = funcName
        bParams.block = block
        bParams.blockNumber = blockNumber
        logger.debug("bParams.funcName")
        logger.debug(bParams.funcName)
        logger.debug("bParams.side_num")
        logger.debug(bParams.side_num)
        # in comment
        bParams.boundName = determineNameOfBoundary(side_num)
        bParams.parsedValues = parsed
        bParams.original = [e.sent for e in eSystem.eqs]
        # END FOR

        vertex.fm = bParams
        return(bParams)
        
    def test(self, block, region, side_num):
        '''
        DESCRIPTION:

        Test if region exist for this side.
        '''
        if side_num == 0:
            # test for left side
            return(region.xfrom == 0.0)
        else:
            # test for right side
            return(region.xto == block.size.sizeX)
