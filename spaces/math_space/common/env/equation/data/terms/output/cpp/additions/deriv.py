# -*- coding: utf-8 -*-
'''
See DESCRIPTION for cppOutsForTerms.get_out_for_termDiff
method first from which one should understand how
params used for choice diff method.

PureDerivGenerator:
INPUT:
general (for all):

blockNumber
derivOrder
indepVarList - var for PureDerivGenerator (like ['x'])
               vars for MixDerivGenerator (like ['x', 'y'])

for params common:
only general

for params special
general +
side
func

for params interconnect (only for PureDerivGenerator)
firstIndex
secondIndexSTR

'''
import sys
from env.equation.data.terms.output.cpp.additions.someFuncs import NewtonBinomCoefficient
from env.equation.data.terms.output.cpp.additions.someFuncs import generateCodeForMathFunction

'''
# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.criminal.someFuncs import NewtonBinomCoefficient
    from domainmode.criminal.someFuncs import generateCodeForMathFunction
else:
    from someFuncs import NewtonBinomCoefficient, generateCodeForMathFunction
'''

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation.py')
logger.setLevel(level=log_level)


class DerivGenerator():
    '''
    DESCRIPTION:
    For debugging.
    '''
    def __init__(self):
        # for debugging:
        self.dbg = True
        self.dbgInx = 5

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                logger.debug(self.dbgInx*' '+str(arg))
            


class PureDerivGenerator(DerivGenerator):
    '''
    DESCRIPTION:
    Find d^{n}(u)/d(x)^{n}
     where n is
      n > 1 for central functions
            (used method common_diff)
      n = 1 or 2 for bound conditions
                 or for interconnect
            (used mehtods special_diff
             or interconnect_diff)

    INPUT:
    See __init__ method.
    
    '''
    def __init__(self, params):
        # for debug
        DerivGenerator.__init__(self)

        # PARAMS FOR ALL
        self.blockNumber = params['blockNumber']

        # shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndex = params['unknownVarIndex']

        # like ['x'] i.e. for which diff maked
        # see in begining of callDerivGenerator
        # TODO use 'x' instead:
        self.indepVarList = params['indepVarList']
        x = self.indepVarList[0]
        self.derivOrder = int(params['indepVarOrders'][x])

        # like ['x', 'y', 'z']
        self.userIndepVariables = ['x', 'y', 'z']
        
        # for method choicing for special
        var = self.indepVarList[0]
        self.indepVarIndexList = [self.userIndepVariables.index(var)]

        # for all
        self.make_general_data()
        # END FOR ALL

        # PARAMS FOR VERTEX:
        if params['diffMethod'] == 'vertex':
            sides = params['vertex_sides']
            if sides == [0, 2]:  # [[0, 2], [2, 1], [1, 3], [3, 0]]
                # for 'x' and 'y' both left side
                self.leftOrRightBoundary = 1
            elif(sides == [2, 1]):
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
            elif(sides == [3, 0]):
                # if 'x'
                if self.indepVarIndexList[0] == 0:
                    # left
                    self.leftOrRightBoundary = 1
                elif(self.indepVarIndexList[0] == 1):
                    # right
                    self.leftOrRightBoundary = 0
            
        # END FOR

        # PARAMS FOR SPECIAL
        # self.parsedMathFunction = params.parsedMathFunction
        
        if params['diffMethod'] == 'special':
            self.side = params['side']

        if ((params['diffMethod'] == 'special')
            and (params['diffType'] == 'pure')):
            self.side = params['side']

            # for debug
            self.print_dbg("FROM PureDerivGenerator.init",
                           "for special")
            self.print_dbg("self.side", self.side)
            self.print_dbg("self.indepVarIndexList",
                           self.indepVarIndexList)

            if ((self.side % 2 == 0)
                and (self.indepVarIndexList[0] == self.side / 2)):
                # left side (0 or 2)
                self.leftOrRightBoundary = 1
            elif ((self.side - 1) % 2 == 0
                  and self.indepVarIndexList[0] == (self.side - 1) / 2):
                # right side (1 or 3)
                self.leftOrRightBoundary = 0
            else:
                # TODO for diffMethod 2d
                self.diffMethod = 'common'
                params.diffMethod = 'common'
                # and same for interconnects
                '''
                raise(SyntaxError("cannot define leftOrRightBoundary"
                                  + " for special_diff: "
                                  + "side = "+str(self.side)
                                  + " VarIndex[0]="+str(self.indepVarIndexList[0])))
                '''

            # for debug
            self.print_dbg("FROM PureDerivGenerator.init",
                           "end for special")

        # END FOR SPECIAL

        # PARAMS FOR INTERCONNECT
        if ((params['diffMethod'] == 'interconnect')
            and (params['diffType'] == 'pure')):

            # for ic[firstIndex][ $ secondIndexSTR $ +
            # in interconnectPureDerivAlternative
            self.side = params['side']
            self.firstIndex = params['firstIndex']
            self.secondIndexSTR = params['secondIndexSTR']
            
            # TODO for diffMethod 2d
            if (((self.side % 2 == 0)
                 and (self.indepVarIndexList[0] == self.side / 2))
                or
                (((self.side - 1) % 2 == 0
                  and self.indepVarIndexList[0] == (self.side - 1) / 2))):
                
                self.diffMethod = 'interconnect'
                params.diffMethod = 'interconnect'
            else:
                self.diffMethod = 'common'
                params.diffMethod = 'common'

        # END FOR INTERCONNECT

        # PARAMS FOR None
        if params['diffMethod'] == 'None':
            # None is depricated
            # that only for errors removing
            self.firstIndex = '{{firstIndex}}'
            self.secondIndexSTR = '{{secondIndexSTR}}'
            self.side = 0
        # END FOR None

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

        USED FUNCTIONS:
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
    
    def diff(self, func=None):
        '''
        DESCRIPTION:
        This fucntion try to find
        method (common, special or interconnect)
        from params. Deprecated.

        parameters
        side,
        firstIndex (for interconnect),
        indepVarIndex[0]
        define choising diff methond.

        USED FUNCTIONS:
        self.indepVarList
        self.blockNumber
        self.firstIndex
        self.side
        
        self.interconnect_diff
        self.common_diff
        self.special_diff
        '''
        # for debug
        self.print_dbg("FROM PureDerivGenerator.diff:")

        # Случай соединения блоков
        if self.firstIndex >= 0:
            if self.side / 2 == self.indepVarIndexList[0]:
                # for debug
                self.print_dbg("interconnect used")

                return self.interconnect_diff()
            else:
                # for debug
                self.print_dbg("common used")

                return self.common_diff()

        # Случай отдельного блока
        else:
            if ((self.side % 2 == 0)
                and (self.indepVarIndexList[0] == self.side / 2)):
                # for debug
                self.print_dbg("special used")

                self.leftOrRightBoundary = 1
                return self.special_diff(func)
            elif ((self.side - 1) % 2 == 0
                  and self.indepVarIndexList[0] == (self.side - 1) / 2):
                # for debug
                self.print_dbg("special used")

                self.leftOrRightBoundary = 0
                return self.special_diff(func)
            else:
                # self.side == -1
                # for debug
                self.print_dbg("common used")

                return self.common_diff()

    def make_general_data(self):
        '''
        DESCRIPTION:
        DXM1 - means dx
        DXM2 - means dx^2
        '''
        self.increment = ('D' + self.indepVarList[0].upper()
                          + 'M' + str(self.derivOrder))
        self.specialIncrement = 'D' + self.indepVarList[0].upper()
        self.stride = ('Block' + str(self.blockNumber)
                       + 'Stride' + self.indepVarList[0].upper())

    def common_diff(self):
        '''
        DESCRIPTION:
        generate cpp derivative for central function
        or for border in case of non border variable
        (for example: for y at border x=0)
        
        for derivOrder = 1
        du/dx = (u_{i+1}-u_{i-1})/(2 dx)
        
        for derivOrder = 2
        ddu/ddx = (u_{i+1}-2*u_{i}+u_{i-1})/(dx^2)

        INPUT
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

    def special_diff(self, func='None'):
        '''
        DESCRIPTION:

        Generate derivative for border variable.
        
        for derivOrder = 1:
        du/dx = phi(t,y)

        for derivOrder = 2:
        left border
        ddu/ddx = 2*(u_{1}-u_{0}-dy*phi(t,y))/(dx^2)
        right border
        ddu/ddx = 2*(u_{n-1}-u_{n}-dy*phi(t,y))/(dx^2)

        INPUT:

        leftOrRightBoundary --- это число либо 0 (если краевое условие наложено на левую границу)
                                либо 1 (если краевое условие наложено на правую границу)
        leftOrRightBoundary = 0 - right border
        leftOrRightBoundary = 1 - left
        specialIncrement - sin(x)*specialIncrement

        USED FUNCTIONS:

        for self.userIndepVariables
        str self.blockNumber
        self.derivOrder
        self.delay
        self.unknownVarIndex
        
        generateCodeForMathFunction
        '''
        # for debug
        self.print_dbg("FROM PureDerivGenerator.special_diff:")

        try:
            increment = self.increment
            specialIncrement = self.specialIncrement
            stride = self.stride
            
        except:
            raise(SyntaxError("use make_general_data first"))

        try:
            # in case if variable direction ortogonal to
            # special border (ex: for side 2, direction y):
            leftOrRightBoundary = self.leftOrRightBoundary
        except:
            # in case if variable direction paralel to
            # special border (ex: for side 2, direction
            # x common_diff must be used):
            return(self.common_diff())

        # for debug
        self.print_dbg("special used")

        fullIndepVarValueList = list([])
        for indepVar in self.userIndepVariables:
            fullIndepVarValueList.extend(['(idx' + indepVar.upper() + ' + Block'
                                          + str(self.blockNumber) + 'Offset'
                                          + indepVar.upper() + ' * D'
                                          + indepVar.upper() + 'M1' + ')'])
        fullIndepVarValueList.extend(['t'])

        # for debug
        self.print_dbg("func:", func)

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
    
    def interconnect_diff(self):
        '''
        DESCRIPTION:
        For connections.
        
        for derivOrder = 1:
        du/dx = (u_{1}-ic[firstIndex][secondIndexSTR])/(2dx)

        for derivOrder = 2:
        ddu/ddx = 2*(u_{1}-2*u_{0}+ic[firstIndex][secondIndexSTR])/(dx^2)
                
        USED FUNCTIONS:

        ic[firstIndex][ $ secondIndexSTR $  +  $ unknownVarIndex[0] $ ]

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
    

class MixDerivGenerator(DerivGenerator):
    '''
    DESCRIPTION:
    Find dd(u)/d(a)d(b)
     where {a, b |a!=b and a,b \in {x, y}}
      common_diff for central functions
      special_diff for bound.

    INPUT:
    params.indepVarList - important parameter, define
                          diff order (i.e ['x','y']
                          means dxdy).
    See __init__ method.


    '''
    def __init__(self, params):
        # for debug
        DerivGenerator.__init__(self)

        # PARAMS FOR ALL
        self.blockNumber = params['blockNumber']

        # shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndex = params['unknownVarIndex']

        # only mix for ddu currently suplied
        self.derivOrder = 2  # params.derivOrder

        # like ['x', 'y', 'z']
        self.userIndepVariables = ['x', 'y', 'z']

        # like ['x', 'y'] i.e. for which diff maked
        # first for 'x', then for 'y' (i.e. diff order)
        # see in begining of callDerivGenerator
        self.indepVarList = params['indepVarList']
        self.indepVarIndexList = range(len(self.indepVarList))
        
        # for all
        self.make_general_data()
        # END FOR ALL

        # FOR SPECIAL
        # self.parsedMathFunction = 'arg_mathFunction'
        self.side = params['side']

        if(params['diffMethod'] == 'special'
           and params['diffType'] == 'mix'):
            try:
                # self.indepVarIndex = params.indepVarIndex
                self.indepVarIndex = self.indepVarList[1]
            except:
                raise(SyntaxError("for special_diff params.indepVarIndex"
                                  + " should be initiated first"))
        # END FOR SPECIAL

    def make_increment_for_varIndex(self, varIndex):
        '''
        DESCRIPTION:
        for varIndex = 'x' or 0 return DXM1
        for varIndex = 'y' or 1 return DYM1
        '''
        if type(varIndex) == int:
            ind = self.indepVarList.index(self.userIndepVariables[varIndex])
        elif(type(varIndex) == str):
            ind = self.indepVarList.index(varIndex)
        self.specialIncrement = ('D' + self.indepVarList[ind].upper()
                                 + 'M' + "1")
        
    def make_general_data(self):
        '''
        DESCRIPTION:
        Make self.increment and self.strideList.
        DXM1 - means dx
        DXM2 - means dx^2

        strideList - [stride of ds_{1}, stride of ds_{2}]
                      where s_{i} \in {x, y, z}

        USED FUNCTIONS:
        self.derivOrder
        self.indepVarList
        '''
        
        increment = '(1 / pow(2,' + str(self.derivOrder) + '))'
        for i, indepVar in enumerate(self.indepVarList):
            increment = (increment + ' * D' + indepVar.upper()
                         + 'M' + str(self.derivOrder))  # + self.derivativeOrderList[i]
        self.increment = increment

        strideList = []
        for indepVar in self.indepVarList:
            strideList.append('Block' + str(self.blockNumber)
                              + 'Stride' + indepVar.upper())

        self.strideList = strideList

    def common_diff(self):
        '''
        DESCRIPTION:
        Способ генерирования кода для смешанной производной для
        CentralFunction и иногда для граничных функций.

        for derivOrder = 2:
        ddu/dxdy = (u(x+1, y+1)-u(x-1, y+1)-u(x+1, y-1)+u(x-1, y-1))/(4*dx^2)

        INPUT:
        strideList - [stride of ds_{1}, stride of ds_{2}]
                     where s_{i} \in {x, y, z}

        USED FUNCTIONS:
        strideList
        self.blockNumber
        self.unknownVarIndex
        '''
        try:
            increment = self.increment
            strideList = self.strideList
        except:
            raise(SyntaxError("increment or strideList are not defined"
                              + "\n use make_general_data first"))

        length = len(strideList)
        if length == 2:
            first = ('source['+'delay'+'][idx+ ('
                     + strideList[0] + ' + ' + strideList[1]
                     + ') * ' + 'Block' + str(self.blockNumber)
                     + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']')
            second = (' - source['+'delay'+'][idx - ('
                      + strideList[0] + ' - ' + strideList[1]
                      + ') * ' + 'Block' + str(self.blockNumber)
                      + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']')
            third = (' - source['+'delay'+'][idx + ('
                     + strideList[0] + ' - ' + strideList[1]
                     + ') * ' + 'Block' + str(self.blockNumber)
                     + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']')
            fourth = (' + source['+'delay'+'][idx - ('
                      + strideList[0] + ' + ' + strideList[1]
                      + ') * ' + 'Block' + str(self.blockNumber)
                      + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']')
            finiteDifference = first + second + third + fourth
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'
        else:
            raise SyntaxError("Order of some mixed partial derivative"
                              + " greater than 2. I don't know how"
                              + " to work with it!")
    
    def special_diff(self, func='None'):
        '''
        DESCRIPTION:
        When used directly (without diff), it things that
        
        ddu/d(a)d(b) = (func(b+1)-func(b-1))/(2d(b))
           where func = du/d(a)
                 a = self.indepVarList[0],
                 b = self.indepVarList[1].
        so indepVarIndex unused.

        INPUT:
        self.indepVarIndex --- это индекс независимой переменной в массиве всех таких переменных;
                               это индекс той переменной, производная по которой
                               входит в смешанную производную второго порядка,
                               но не той переменной, для которой написано краевое условие Неймана.
                               0 - for dydx or dzdx
                               1 - for dxdy or dzdy
                               2 - for dxdz or dydz
        
        FOR EXAMPLE:
        for derivOrder = 2 
        and self.indepVarList=['x','y']:
        ddu/dxdy = (phi(y+1)-phi(y-1))/(2dy)
           for phi(x,y)=du/dx

        USED FUNCTIONS:
        self.userIndepVariables
        self.blockNumber
        self.func
        '''
        # for debug
        self.print_dbg("FROM MixDerivGenerator.special_diff:")

        try:
            indepVarIndex = self.indepVarIndex
        except:
            raise(SyntaxError("for special_diff self.indepVarIndex"
                              + "should be initiated first"))
        if type(indepVarIndex) == str:
            indepVarIndex = self.userIndepVariables.index(indepVarIndex)

        # find increment
        self.make_increment_for_varIndex(indepVarIndex)
        increment = self.specialIncrement
    
        if self.derivOrder == 2:
            right = func
            left = func
            for k, indepVar in enumerate(self.userIndepVariables):
                # phase args into func
                if ('arg_'+indepVar.upper()) in func:
                    if k == indepVarIndex:
                        argNewR = ('(idx' + indepVar.upper()
                                   + ' + Block' + str(self.blockNumber)
                                   + 'Offset' + indepVar.upper()
                                   + ' * D' + indepVar.upper()
                                   + 'M1' + ' + 1)')
                        argNewL = ('(idx' + indepVar.upper()
                                   + ' + Block' + str(self.blockNumber)
                                   + 'Offset' + indepVar.upper()
                                   + ' * D' + indepVar.upper()
                                   + 'M1' + ' - 1)')
                        right = right.replace('arg_'+indepVar.upper(),
                                              argNewR)
                        left = left.replace('arg_'+indepVar.upper(),
                                            argNewL)
                    else:
                        argNewR = ('(idx' + indepVar.upper()
                                   + ' + Block' + str(self.blockNumber)
                                   + 'Offset' + indepVar.upper()
                                   + ' * D' + indepVar.upper()
                                   + 'M1' + ')')
                        argNewL = ('(idx' + indepVar.upper()
                                   + ' + Block' + str(self.blockNumber)
                                   + 'Offset' + indepVar.upper()
                                   + ' * D' + indepVar.upper()
                                   + 'M1' + ')')

                        right = right.replace('arg_'+indepVar.upper(),
                                              argNewR)
                        left = left.replace('arg_'+indepVar.upper(),
                                            argNewL)
            if 'arg_T' in func:
                right = right.replace('arg_T',
                                      't')
                left = left.replace('arg_T',
                                    't')

            # for debug
            self.print_dbg("left:", left)
            self.print_dbg("right:", right)
            self.print_dbg("indepVarIndex:",
                           indepVarIndex)

            if right == left:
                return '0.0'
            else:
                return('(0.5 * ' + increment + ' * '
                       + '(' + '(' + right + ')' + ' - '
                       + '(' + left + ')' + ')' + ')')
        else:
            raise SyntaxError("The highest derivative order of"
                              + " the system greater than 2!"
                              + " I don't know how to generate"
                              + " boundary function in this case!")
    
    def diff(self, func=None):
        '''
        DESCRIPTION:
        This fucntion try to find
        method (common, special)
        from params. Deprecated.

        For 2d work fine
        For 3d not work.

        USED FUNCTIONS:
        self.indepVarList - for order of diff
                            (i.e. dxdy or dydx)
        self.userIndepVariables
        self.side
        
        '''
        # (0, y, 0) or (x_max, y, 0)
        bCond1 = self.side == 0 or self.side == 1
        # (x, 0, 0) or (x, y_max, 0)
        bCond2 = self.side == 2 or self.side == 3
        # (0, 0, z) or (x_max, 0, z)
        bCond3 = self.side == 4 or self.side == 5

        # check if diff vars either dxdy or dydx
        indepVarCond1 = ((self.indepVarList[0] == self.userIndepVariables[0]
                          and self.indepVarList[1] == self.userIndepVariables[1])
                         or (self.indepVarList[1] == self.userIndepVariables[0]
                             and self.indepVarList[0] == self.userIndepVariables[1]))
        # self.blockDimension
        blockDimension = len(self.userIndepVariables)
        if blockDimension > 2:
            # check if diff vars either dxdz or dzdx
            indepVarCond2 = ((self.indepVarList[0] == self.userIndepVariables[0]
                              and self.indepVarList[1] == self.userIndepVariables[2])
                             or (self.indepVarList[1] == self.userIndepVariables[0]
                                 and self.indepVarList[0] == self.userIndepVariables[2]))
            # check if diff vars either dydz or dzdy
            indepVarCond3 = ((self.indepVarList[0] == self.userIndepVariables[1]
                              and self.indepVarList[1] == self.userIndepVariables[2])
                             or (self.indepVarList[1] == self.userIndepVariables[1]
                                 and self.indepVarList[0] == self.userIndepVariables[2]))
        
        if ((bCond1 and indepVarCond1)
            or (blockDimension > 2 and bCond3 and indepVarCond3)):
            '''
            either
             dim = 2 and ((0, y) or (x_max, y)) and (dxdy or dydx)
             and phi = du/dx
            or
             dim = 3 and ((0, 0, z) or (x_max, 0, z)) and (dydz or dzdy)
             and phi = du/dy (or du/dx)
            '''
            # for dxdy
            # ddu/dxdy=(u(x,y+1)-u(x,y-1))/dy
            # or dzdy
            # ddu/dydz=(u(x,y,z+1)-u(x,y,z-1))/dz
            self.indepVarIndex = 'y'
            return self.special_diff(func)
        elif ((blockDimension > 2 and bCond1 and indepVarCond2)
              or (blockDimension > 2 and bCond2 and indepVarCond3)):
            '''
            either
             dim = 3 and ((0, y, 0) or (x_max, y, 0)) and (dxdz or dzdx)
             and phi = du/dx
            or
             dim = 3 and ((x, 0, 0) or (x, y_max, 0)) and (dydz or dzdy)
             and phi = du/dy (should be dydx)
            '''
            # for dxdz or dydz
            # ddu/dxdz = (u(x,y,z+1)-u(x,y,z-1))/dz
            # ddu/dydz=(u(x,y,z+1)-u(x,y,z-1))/dz
            self.indepVarIndex = 'z'
            return self.special_diff(func)
        elif ((bCond2 and indepVarCond1)
              or (blockDimension > 2 and bCond3 and indepVarCond2)):
            '''
            either
             dim = 2 and ((x, 0) or (x, y_max)) and (dxdy or dydx)
             and phi = du/dy
            or ???
             dim = 3 and ((0, 0, z) or (x_max, 0, z)) and (dxdz or dzdx)
             and must phi = du/dx (or du/dy) but have phi = du/dz
            '''
            # for dydx
            # ddu/dydx=(u(x+1,y)-u(x-1,y))/dx
            # or dzdx ???
            # ddu/dydx=(u(x+1,y,z)-u(x-1,y,z))/dx
            self.indepVarIndex = 'x'
            return self.special_diff(func)
        else:
            return self.common_diff()


class TestCase():
    def __init__(self):
        params = {'unknownVarIndex': 0,
                  'blockNumber': 0,
                  'indepVarList': ['x'],
                  'side': 0,
                  'derivOrder': 2,
                  'diffType': 'pure',
                  'diffMethod': 'vertex'}
        '''
        class Params():
            def __init__(self):
                self.unknownVarIndex = 0
                self.blockNumber = 0
                self.indepVarList = ['x']
                self.side = 0
                self.derivOrder = 2
                self.diffType = 'pure'
                self.diffMethod = 'vertex'
        self.params = Params()
        '''
        self.params = params

    def test_diff_vertex(self):
        self.params['vertex_sides'] = [2, 1]
        print("for vertex")
        print(self.params['vertex_sides'])

        func = "func"

        print("for x")
        self.params['indepVarList'] = ['x']
        self.gen = PureDerivGenerator(self.params)
        
        print(self.gen.special_diff(func))
        
        print("for y")
        self.params['indepVarList'] = ['y']
        self.gen = PureDerivGenerator(self.params)
        
        print(self.gen.special_diff(func))

    def test_diff_special(self):
        self.gen = PureDerivGenerator(self.params)

        func = "func"
        print(self.gen.special_diff(func))
    
