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
    .cpp.additions.deriv.gen_pure_borders import GenPureBorders

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_pure_ics.py')
logger.setLevel(level=log_level)


class GenPureIcs(GenPureBorders):
    '''
    DESCRIPTION:

    Find d^{n}(u)/d(x)^{n}
     where n is
      n = 1 or 2 for interconnect
            (used ics_diff)

    INPUT:

    See ``self.__init__``
    
    '''
    def __init__(self, blockNumber, unknownVarIndex,
                 indepVar, indepVarOrders):
        GenPureBorders.__init__(self, blockNumber, unknownVarIndex,
                                indepVar, indepVarOrders)

    def set_special_params(self, side, firstIndex, secondIndexSTR):
        
        '''
        in case of 1d sides: 0, 1
        for ic[firstIndex][ $ secondIndexSTR $ +
        '''
        # FOR SPECIAL PARAMS:
        self.side = side
        self.firstIndex = firstIndex
        self.secondIndexSTR = secondIndexSTR
        # END FOR

    def ics_diff(self):
        '''
        DESCRIPTION:

        For connections.
        
        for derivOrder = 1 and left sides (0, 2):
        
        .. math:: du/dx = (u_{1}-ic[firstIndex][secondIndexSTR])/(2dx)


        for derivOrder = 1 and right sides (1, 3):
        
        .. math:: du/dx = (ic[firstIndex][secondIndexSTR]-u_{n-1})/(2dx)

        for derivOrder = 2 and left sides (0, 2):

        .. math:: ddu/ddx = 2*(u_{1}-2*u_{0}
        +ic[firstIndex][secondIndexSTR])/(dx^2)
        
        for derivOrder = 2 and right sides (1, 3):

        .. math:: ddu/ddx = 2*(ic[firstIndex][secondIndexSTR]-2*u_{n}
        +u_{n-1})/(dx^2)
        
        Return:

        ic[firstIndex][ $ secondIndexSTR $  +  $ unknownVarIndex[0] $ ]

        USED FUNCTIONS::

            self.side
            self.delay
            str self.blockNumber
            str self.firstIndex for ic[firstIndex]
            self.secondIndexSTR
            str self.unknownVarIndex
            self.derivOrder
        '''

        try:
            increment = self.increment
            stride = self.stride
        except:
            raise(SyntaxError("increment or stride are not defined"
                              + "\n use make_general_data first"))

        if self.is_special_case() < 0:
            # in case if variable direction parallel to
            # ic border (ex: for side 2, direction
            # x) common_diff must be used:
            return(self.common_diff())

        if self.side % 2 == 0:
            first = ('source['+'delay'+'][idx + '
                     + stride + ' * ' + 'Block'
                     + str(self.blockNumber) + 'CELLSIZE + '
                     + str(self.unknownVarIndex) + ']')
            second = ('ic['+str(self.firstIndex)+']['
                      + str(self.secondIndexSTR) + ' + '
                      + str(self.unknownVarIndex) + ']')
        else:
            first = ('ic['+str(self.firstIndex)+']['
                     + str(self.secondIndexSTR) + ' + '
                     + str(self.unknownVarIndex) + ']')
            second = ('source['+'delay'+'][idx - '
                      + stride + ' * ' + 'Block'
                      + str(self.blockNumber) + 'CELLSIZE + '
                      + str(self.unknownVarIndex) + ']')
        if self.derivOrder == 1:
            return('0.5 * ' + increment + ' * '
                   + '(' + first + ' - ' + second + ')')
        elif self.derivOrder == 2:
            third = ('2.0 * source['+'delay'+'][idx + '
                     + str(self.unknownVarIndex) + ']')
            return('(' + increment + ' * '
                   + ('(' + first + ' - ' + third + ' + '
                      + second + ')')
                   + ')')
        else:
            raise AttributeError("Pure derivative in some equation"
                                 + " has order greater than 2!")
    
