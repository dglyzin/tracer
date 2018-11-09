import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from env.equation.data.terms.output \
    .cpp.additions.someFuncs import NewtonBinomCoefficient
from env.equation.data.terms.output \
    .cpp.additions.deriv.gen_pure_common import GenPureCommon

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_pure_borders.py')
logger.setLevel(level=log_level)


class GenPureBorders(GenPureCommon):
    '''
    DESCRIPTION:

    Find d^{n}(u)/d(x)^{n}
     where n is
      n = 1 or 2 for bound conditions
            (used interconnect_diff)

    INPUT:

    See ``self.__init__``
    
    '''
    def __init__(self, blockNumber, unknownVarIndex,
                 indepVar, indepVarOrders):
        GenPureCommon.__init__(self, blockNumber, unknownVarIndex,
                               indepVar, indepVarOrders)

    def set_special_params(self, side):
        
        '''
        in case of 1d sides: 0, 1
        '''
        # FOR SPECIAL PARAMS:
        self.side = side

        # for debug
        logger.debug("FROM set_special_params")
        logger.debug("for special")
        logger.debug("self.side: %s" % str(self.side))
        logger.debug("self.indepVarIndexList %s"
                     % str(self.indepVarIndexList))

        # for debug
        logger.debug("FROM set_special_params")
        logger.debug("end for special")
        # END FOR SPECIAL

    def is_special_case(self):

        '''In case if variable direction is orthogonal
        to border (ex: for side 2, direction y) return
        positive_or_zero.
        In case if variable direction parallel to
        special border (ex: for side 2, direction x)
        return negative.
        (so common_diff must be used)
        where positive_or_zero is:

        leftOrRightBoundary --- это число либо 1 (если краевое условие наложено на левую границу)
                                либо 0 (если краевое условие наложено на правую границу)
        leftOrRightBoundary = 0 - right border
        leftOrRightBoundary = 1 - left

        in case of 1d sides: 0, 1

        Tests:

        >>> f = lambda side, index: True if (side % 2 == 0 \
        and index == side // 2) \
        or ((side-1)%2==0 and index == (side-1)//2) else False

        >>> f(0, ['x', 'y'].index('x'))
        True

        >>> f(1, ['x', 'y'].index('x'))
        True

        >>> f(2, ['x', 'y'].index('x'))
        False

        >>> f(3, ['x', 'y'].index('x'))
        False

        >>> f(3, ['x', 'y'].index('y'))
        True

        >>> f(2, ['x', 'y'].index('y'))
        True

        >>> f(1, ['x', 'y'].index('y'))
        False

        >>> f(0, ['x', 'y'].index('y'))
        False
        '''
        try:
            self.side
        except AttributeError:
            raise(SyntaxError("use set_special_params first"))

        # TODO for diffMethod 3d
        if (((self.side % 2 == 0)
             and (self.indepVarIndexList[0] == self.side // 2))):
            # left side (0 or 2)
            return(1)
            
        elif((self.side - 1) % 2 == 0
             and self.indepVarIndexList[0] == (self.side - 1) // 2):
            # right side (1 or 3)
            return(0)
        else:
            return(-1)

    def get_boundary(self):
        
        '''In case if variable direction is orthogonal
        to border (ex: for side 2, direction y) return
        positive_or_zero.
        In case if variable direction parallel to
        special border (ex: for side 2, direction x)
        return negative.
        (so common_diff must be used)
        where positive_or_zero is:

        leftOrRightBoundary --- это число либо 1 (если краевое условие наложено на левую границу)
                                либо 0 (если краевое условие наложено на правую границу)
        leftOrRightBoundary = 0 - right border
        leftOrRightBoundary = 1 - left

        in case of 1d sides: 0, 1
        '''
        leftOrRightBoundary = self.is_special_case()
        return(leftOrRightBoundary)

        '''
        if ((self.side % 2 == 0)
            and (self.indepVarIndexList[0] == self.side / 2)):
            # left side (0 or 2)
            self.leftOrRightBoundary = 1
        elif ((self.side - 1) % 2 == 0
              and self.indepVarIndexList[0] == (self.side - 1) / 2):
            # right side (1 or 3)
            self.leftOrRightBoundary = 0
        else:
            return(None)
        return(self.leftOrRightBoundary)
        '''

    def borders_diff(self, func='None'):
        '''
        DESCRIPTION:

        Generate derivative for border variable.
        
        for derivOrder = 1:
        du/dx = phi(t,y)

        for derivOrder = 2:
        left border

        .. math:: ddu/ddx = 2*(u_{1}-u_{0}-dy*phi(t,y))/(dx^2)
        
        right border
        
        .. math:: ddu/ddx = 2*(u_{n-1}-u_{n}-dy*phi(t,y))/(dx^2)

        INPUT:

        leftOrRightBoundary --- это число либо 0 (если краевое условие наложено на левую границу)
                                либо 1 (если краевое условие наложено на правую границу)
        leftOrRightBoundary = 0 - right border
        leftOrRightBoundary = 1 - left
        specialIncrement - sin(x)*specialIncrement

        USED FUNCTIONS::

            for self.userIndepVariables
            str self.blockNumber
            self.derivOrder
            self.delay
            self.unknownVarIndex

            generateCodeForMathFunction
        '''
        # for debug
        logger.debug("FROM GenPureBorders.borders_diff:")

        try:
            increment = self.increment
            specialIncrement = self.specialIncrement
            stride = self.stride
            
        except AttributeError:
            raise(SyntaxError("use make_general_data first"))

        # in case if variable direction is orthogonal
        # to border (ex: for side 2, direction y):
        leftOrRightBoundary = self.get_boundary()
        if leftOrRightBoundary < 0:
            # in case if variable direction parallel to
            # special border (ex: for side 2, direction
            # x) common_diff must be used:
            return(self.common_diff())

        # for debug
        logger.debug("special used")

        fullIndepVarValueList = list([])
        for indepVar in self.userIndepVariables:
            fullIndepVarValueList.extend(['(idx' + indepVar.upper() + ' + Block'
                                          + str(self.blockNumber) + 'Offset'
                                          + indepVar.upper() + ' * D'
                                          + indepVar.upper() + 'M1' + ')'])
        fullIndepVarValueList.extend(['t'])

        # for debug
        logger.debug("func: %s" % func)

        boundaryValue = func

        if self.derivOrder == 1:
            return boundaryValue
        elif self.derivOrder == 2:
            second = ('source['+'delay'+'][idx + '
                      + str(self.unknownVarIndex) + ']')
            m1 = leftOrRightBoundary % 2
            m2 = (leftOrRightBoundary - 1) % 2
            first = ('source['+'delay'+'][idx' + m1 * ' + '
                     + m2 * ' - ' + stride + ' * ' + 'Block'
                     + str(self.blockNumber) + 'CELLSIZE + '
                     + str(self.unknownVarIndex) + ']')
            return('(2.0 * '+increment+' * '+'('+first+' - '
                   + second + m1 * ' - ' + m2 * ' + ' +
                   '(' + boundaryValue + ') * '
                   + specialIncrement + '))')
        else:
            raise SyntaxError("The highest derivative order of"
                              + " the system greater than 2!"
                              + " I don't know how to generate"
                              + " boundary function in this case!")
    

