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

from env.equation.data.terms.output.cpp.additions.someFuncs import NewtonBinomCoefficient

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_pure_common.py')
logger.setLevel(level=log_level)


class GenPureCommon():
    '''
    DESCRIPTION:

    Find d^{n}(u)/d(x)^{n}
     where n is
      n > 1 for central functions
            (used method common_diff)

    INPUT:

    See ``self.__init__``
    
    '''
    def __init__(self, blockNumber, unknownVarIndex,
                 indepVar, indepVarOrders):

        '''
        Inputs:
        
        - ``blockNumber`` -- used for strides and cellsize
        variables names

        - ``unknownVarIndex`` -- shift index for variable
        (like (U, V)-> (source[+0], source[+1]))
        (Ex: dict([('U', 0), ('V', 1)])['U'])

        - ``indepVar`` -- like 'x' i.e. for which diff maked

        - ``indepVarOrders`` -- dict([(var, float(order))])
        
        '''

        # PARAMS FOR ALL
        self.blockNumber = blockNumber

        # shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndex = unknownVarIndex

        # like ['x'] i.e. for which diff maked
        # see in begining of callDerivGenerator
        # TODO use 'x' instead:
        self.indepVar = indepVar
        x = self.indepVar

        logger.debug("indepVarOrders:")
        logger.debug(indepVarOrders)

        self.derivOrder = int(indepVarOrders[x])

        # like ['x', 'y', 'z']
        self.userIndepVariables = ['x', 'y', 'z']
        
        # for method choosing for special
        var = self.indepVar
        self.indepVarIndexList = [self.userIndepVariables.index(var)]

        # for all
        self.make_general_data()
        # END FOR ALL

    def make_general_data(self):
        '''
        DESCRIPTION:
        DXM1 - means dx
        DXM2 - means dx^2
        '''
        self.increment = ('D' + self.indepVar.upper()
                          + 'M' + str(self.derivOrder))
        self.specialIncrement = 'D' + self.indepVar.upper()
        self.stride = ('Block' + str(self.blockNumber)
                       + 'Stride' + self.indepVar.upper())

    def createIndicesList(self):
        '''
        DESCRIPTION:

        Т.к. для CentralFunction умеем генерировать аппроксимации
        производных любого порядка, то эти аппроксимации содержат
        много слагаемых, каждое из которых имеет свой индекс.

        EXAMPLES:

        For derivOrder = 1
        [' + 0', '-1']
        
        For derivOrder = 2
        [' + 1', ' + 0', '-1']

        For derivOrder = 3
        [' + 1', ' + 0', '-1', '-2']

        USED FUNCTIONS::

            self.derivOrder
        '''
        leftIndex = self.derivOrder // 2
        rightIndex = -(self.derivOrder - leftIndex)
        reverseList = [i for i in range(rightIndex, leftIndex + 1)]
        comfortableList = reverseList[::-1]
        indicesListAsString = []
        for index in comfortableList:
            if index >= 0:
                indicesListAsString.extend([' + ' + str(int(index))])
            else:
                indicesListAsString.extend([str(int(index))])
        return indicesListAsString
    
    def createCoefficientList(self):
        '''
        DESCRIPTION:

        Т.к. для CentralFunction умеем генерировать аппроксимации
        производных любого порядка, то эти аппроксимации содержат
        много слагаемых, перед каждым из которых имеется свой
        коэффициент.

        Create Newton binom coefficients

        self.derivOrder
        '''
        numberList = [NewtonBinomCoefficient(self.derivOrder, k)
                      for k in range(0, self.derivOrder + 1)]
        stringList = []
        for number in numberList:
            stringList.extend([str(number)])
        return stringList

    def common_diff(self):
        '''
        DESCRIPTION:

        generate cpp derivative for central function
        or for border in case of non border variable
        (for example: for y at border x=0)
        
        for ``derivOrder = 1``:

        .. math::  du/dx = (u_{i+1}-u_{i-1})/(2 dx)
        
        for ``derivOrder = 2``:

        .. math:: ddu/ddx = (u_{i+1}-2*u_{i}+u_{i-1})/(dx^2)

        Template:

        source[idx  # point in that derive will find
        +  stride  * Block0CELLSIZE  # +1 to some of {x,y,z} direction
                                     # (defined by stride)
                                     # ('x': +1,
                                     #  'y': + Block0StrideY*Block0CELLSIZE,
                                     #  'z': + Block0StrideZ*Block0CELLSIZE
                                     #         = Block0SizeY*Block0CountY*Block0CELLSIZE)
        +  $ unknownVarIndex[0] $ ]  # shift, differ for each variable ('U': +0, 'V': +1)
        
        USED FUNCTIONS:

        str self.blockNumber
        self.delay
        str self.unknownVarIndex
        
        self.createIndicesList
        self.createCoefficientList
        
        '''
        try:
            increment = self.increment
            stride = self.stride
        except:
            raise(SyntaxError("increment or stride are not defined"
                              + "\n use make_general_data first"))

        if self.derivOrder == 1:
            toLeft = ('source['+'delay'+'][idx - '
                      + stride + ' * ' + 'Block'
                      + str(self.blockNumber) + 'CELLSIZE + '
                      + str(self.unknownVarIndex) + ']')
            toRight = ('source['+'delay'+'][idx + '
                       + stride + ' * ' + 'Block'
                       + str(self.blockNumber) + 'CELLSIZE + '
                       + str(self.unknownVarIndex) + ']')
            return('0.5 * ' + increment + ' * '
                   + '(' + toRight + ' - ' + toLeft + ')')
        else:
            indicesList = self.createIndicesList()
            coefficientList = self.createCoefficientList()
            finiteDifference = ''
            for i, index in enumerate(indicesList):
                m1 = i % 2
                m2 = (i + 1) % 2
                m3 = i > 0
                m4 = coefficientList[i] != '1.0'
                startOfLine = (finiteDifference
                               + m1 * ' - ' + m2 * m3 * ' + '
                               + m4 * (str(coefficientList[i])
                                       + ' * '))
                restOfLine = ('source['+'delay'+'][idx' + str(index)
                              + ' * ' + stride + ' * ' + 'Block'
                              + str(self.blockNumber) + 'CELLSIZE + '
                              + str(self.unknownVarIndex) + ']')
                finiteDifference = startOfLine + restOfLine
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'

