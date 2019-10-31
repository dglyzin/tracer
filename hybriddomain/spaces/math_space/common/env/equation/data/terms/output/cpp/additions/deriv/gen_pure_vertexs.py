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

from env.equation.data.terms.output \
    .cpp.additions.someFuncs import NewtonBinomCoefficient
from env.equation.data.terms.output \
    .cpp.additions.deriv.gen_pure_borders import GenPureBorders

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_pure_vertexs.py')
logger.setLevel(level=log_level)


class GenPureVertexs(GenPureBorders):
    '''
    DESCRIPTION:

    Find d^{n}(u)/d(x)^{n}
     where n is
      n = 1 or 2 for vertexs conditions
            (used vertexs_diff)

    INPUT:

    See ``self.__init__``
    
    '''
    def __init__(self, blockNumber, unknownVarIndex,
                 indepVar, indepVarOrders):
        GenPureBorders.__init__(self, blockNumber, unknownVarIndex,
                                indepVar, indepVarOrders)

    def set_special_params(self, vertex_sides):
        
        '''
        in case of 1d sides: 0, 1
        '''
        # PARAMS FOR VERTEX:
        self.vertex_sides = vertex_sides
        
    def get_boundary(self):

        sides = self.vertex_sides[:]
        sides.sort()
        logger.debug("sides:")
        logger.debug(sides)

        if sides == [0, 2]:  # [[0, 2], [2, 1], [1, 3], [3, 0]]
            # for 'x' and 'y' both left side
            self.leftOrRightBoundary = 1
        elif(sides == [1, 2]):
            # if 'x'
            if self.indepVarIndexList[0] == 0:
                # right
                self.leftOrRightBoundary = 0
            elif(self.indepVarIndexList[0] == 1):
                # left
                self.leftOrRightBoundary = 1
        elif(sides == [1, 3]):
            # for 'x' and 'y' both right side
            self.leftOrRightBoundary = 0
        elif(sides == [0, 3]):
            # if 'x'
            if self.indepVarIndexList[0] == 0:
                # left
                self.leftOrRightBoundary = 1
            elif(self.indepVarIndexList[0] == 1):
                # right
                self.leftOrRightBoundary = 0
        # END FOR
        return(self.leftOrRightBoundary)

    def vertexs_diff(self, func='None'):

        '''
        DESCRIPTION:

        Generate derivative for vertex variable.
        
        for derivOrder = 1:
        du/dx = phi(t,y)

        for derivOrder = 2:
        left border

        .. math:: ddu/ddx = 2*(u_{1}-u_{0}-dy*phi(t,y))/(dx^2)
        
        right border
        
        .. math:: ddu/ddx = 2*(u_{n-1}-u_{n}-dy*phi(t,y))/(dx^2)

        '''
        
        return(self.borders_diff(func))
