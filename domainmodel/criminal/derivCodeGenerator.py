# -*- coding: utf-8 -*-
from someFuncs import NewtonBinomCoefficient, generateCodeForMathFunction

class PureDerivGenerator:
    '''
    DESCRIPTION:
    side 
    and 
    firstIndex 
    and
    indepVarIndexList[0]
    define choising diff methond.

    '''
    def __init__(self, params):
        self.blockNumber = params.blockNumber

        # shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndex = params.unknownVarIndex

        # like ['x'] i.e. for which diff maked
        # see in begining of callDerivGenerator
        self.indepVarList = params.indepVarList
        self.indepVarIndexList = params.indepVarIndexList
        
        self.derivOrder = params.derivOrder

        # like ['x', 'y', 'z']
        self.userIndepVariables = params.userIndepVariables

        self.parsedMathFunction = params.parsedMathFunction
        self.side = params.side

        # for ic[firstIndex][ $ secondIndexSTR $ +
        # in interconnectPureDerivAlternative
        self.firstIndex =  params.firstIndex
        self.secondIndexSTR = params.secondIndexSTR

        # for delays:
        self.delay = str(params.delay)
    
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
    
    def pureDerivative(self):
        '''
        DESCRIPTION:
        side 
        and 
        firstIndex 
        and
        indepVarIndexList[0]
        define choising diff methond.

        USED FUNCTIONS:
        self.indepVarList
        self.blockNumber
        self.firstIndex
        self.side
        
        self.interconnectPureDerivAlternative
        self.commonPureDerivativeAlternative
        self.specialPureDerivativeAlternative
        '''
        increment = self.increment
        specialIncrement = self.specialIncrement
        stride = self.stride
        
        # Случай соединения блоков
        if self.firstIndex >= 0:
            if self.side / 2 == self.indepVarIndexList[0]:
                print("interconnect used")
                return self.interconnectPureDerivAlternative(increment, stride)
            else:
                print('common used')
                return self.commonPureDerivativeAlternative(increment, stride)

        # Случай отдельного блока
        else:
            if ((self.side % 2 == 0)
                and (self.indepVarIndexList[0] == self.side / 2)):
                return self.specialPureDerivativeAlternative(increment, specialIncrement,
                                                             stride, 1)
            elif ((self.side - 1) % 2 == 0
                  and self.indepVarIndexList[0] == (self.side - 1) / 2):
                return self.specialPureDerivativeAlternative(increment, specialIncrement,
                                                             stride, 0)
            else:
                return self.commonPureDerivativeAlternative(increment, stride)

    def make_general_data(self):
        self.increment = ('D' + self.indepVarList[0].upper()
                          + 'M' + str(self.derivOrder))
        self.specialIncrement = 'D' + self.indepVarList[0].upper()
        self.stride = ('Block' + str(self.blockNumber)
                       + 'Stride' + self.indepVarList[0].upper())

    def commonPureDerivativeAlternative(self, increment, stride):
        '''
        DESCRIPTION:
        generate cpp derivative for central function
        or for border in case of non border variable
        (for example: for y at border x=0)
        
        for derivOrder = 1
        du/dx = (u_{i+1}-u_{i-1})/(2 dx)
        
        for dericOrder = 2
        ddu/ddx = (u_{i+1}-2*u_{i}+u_{i-1})/(dx^2)

        source[idx  # point in that derive will find
        +  stride  * Block0CELLSIZE  # +1 to some of {x,y,z} direction 
                                     # (defined by stride) 
                                     # ('x': +1,
                                     #  'y': + Block0StrideY*Block0CELLSIZE,
                                     #  'z': + Block0StrideZ*Block0CELLSIZE
                                     #         = Block0SizeY*Block0CountY*Block0CELLSIZE)
        +  $ unknownVarIndex[0] $ ] # +1 for each variable ('U': +0, 'V': +1)
        
        USED FUNCTIONS:
        str self.blockNumber
        self.delay
        str self.unknownVarIndex
        
        self.createIndicesList
        self.createCoefficientList
        
        '''
        if self.derivOrder == 1:
            toLeft = ('source['+self.delay+'][idx - '
                      + stride + ' * ' + 'Block'
                      + str(self.blockNumber) + 'CELLSIZE + '
                      + str(self.unknownVarIndex) + ']')
            toRight = ('source['+self.delay+'][idx + '
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
                restOfLine = ('source['+self.delay+'][idx' + str(index)
                              + ' * ' + stride + ' * ' + 'Block'
                              + str(self.blockNumber) + 'CELLSIZE + '
                              + str(self.unknownVarIndex) + ']')
                finiteDifference = startOfLine + restOfLine
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'

    def specialPureDerivativeAlternative(self, increment, specialIncrement, stride, leftOrRightBoundary):
        '''
        DESCRIPTION:
        Generate derivative for border variable.
        
        for derivOrder = 1:
        du/dx = phi(t,y)

        for derivOrder = 2:
        ddy/ddx = 2*(u_{1}-u_{0}-dy*phi(t,y))/(dx^2)
        
        INPUT:
        leftOrRightBoundary --- это число либо 0 (если краевое условие наложено на левую границу)
                                либо 1 (если краевое условие наложено на правую границу)
        specialIncrement - sin(x)*specialIncrement

        USED FUNCTIONS:
        for self.userIndepVariables
        str self.blockNumber
        self.derivOrder
        self.delay
        self.unknownVarIndex
        
        generateCodeForMathFunction
        '''
        print("specialPureDerivativeAlternative used")
        fullIndepVarValueList = list([])
        for indepVar in self.userIndepVariables:
            fullIndepVarValueList.extend(['(idx' + indepVar.upper() + ' + Block'
                                          + str(self.blockNumber) + 'Offset'
                                          + indepVar.upper() + ' * D'
                                          + indepVar.upper() + 'M1' + ')'])
        fullIndepVarValueList.extend(['t'])
        
        print("parsedMathFunction from special=")
        print(self.parsedMathFunction)

        boundaryValue = 'generateCodeForMathFunction'

        if self.derivOrder == 1:
            return boundaryValue
        elif self.derivOrder == 2:
            second = ('source['+self.delay+'][idx + '
                      + str(self.unknownVarIndex) + ']')
            m1 = leftOrRightBoundary % 2
            m2 = (leftOrRightBoundary - 1) % 2
            first = ('source['+self.delay+'][idx' + m1 * ' + '
                     + m2 * ' - ' + stride + ' * ' + 'Block'
                     + str(self.blockNumber) + 'CELLSIZE + '
                     + str(self.unknownVarIndex) + ']')
            return('(2.0 * '+increment+' * '+'('+first+' - '
                   + second+ m1 * ' - ' + m2 * ' + ' +
                   '(' + boundaryValue + ') * '
                   + specialIncrement + '))')
        else:
            raise SyntaxError("The highest derivative order of"
                              + " the system greater than 2!"
                              + " I don't know how to generate"
                              + " boundary function in this case!")
    
    def interconnectPureDerivAlternative(self, increment, stride):
        '''
        DESCRIPTION:
        For connections.
        
        for derivOrder = 1:
        du/dx = (u_{1}-ic[firstIndex][secondIndexSTR])/(2dx)

        for derivOrder = 2:
        ddy/ddx = 2*(u_{1}-2*u_{0}+ic[firstIndex][secondIndexSTR])/(dx^2)
        
        
        
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
        if self.side % 2 == 0:
            first = ('source['+self.delay+'][idx + '
                     + stride + ' * ' + 'Block'
                     + str(self.blockNumber) + 'CELLSIZE + '
                     + str(self.unknownVarIndex) + ']')
            second = ('ic['+str(self.firstIndex)+']['
                      + self.secondIndexSTR + ' + '
                      + str(self.unknownVarIndex) + ']')
        else:
            first = ('ic['+str(self.firstIndex)+']['
                     + self.secondIndexSTR + ' + '
                     + str(self.unknownVarIndex) + ']')
            second = ('source['+self.delay+'][idx - '
                      + stride + ' * ' + 'Block'
                      + str(self.blockNumber) + 'CELLSIZE + '
                      + str(self.unknownVarIndex) + ']')
        if self.derivOrder == 1:
            return('0.5 * ' + increment + ' * '
                   + '(' + first + ' - ' + second + ')')
        elif self.derivOrder == 2:
            third = ('2.0 * source['+self.delay+'][idx + '
                     + str(self.unknownVarIndex) + ']')
            return('(' + increment + ' * '
                   + ('(' + first + ' - ' + third + ' + '
                      + second + ')')
                   + ')')
        else:
            raise AttributeError("Pure derivative in some equation"
                                 + " has order greater than 2!")
    
class MixDerivGenerator:
    def __init__(self, blockNumber, unknownVarIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex, secondIndexSTR, delay):
        self.blockNumber = blockNumber
        self.unknownVarIndex = unknownVarIndex
        self.indepVarList = indepVarList
        self.indepVarIndexList = indepVarIndexList
        self.derivativeOrderList = derivativeOrderList
        
        self.derivOrder = 0
        for order in self.derivativeOrderList:
            self.derivOrder += int(order)
        
        self.userIndepVariables = userIndepVariables
        self.parsedMathFunction = parsedMathFunction
        self.side = side
        self.firstIndex=  firstIndex
        self.secondIndexSTR = secondIndexSTR
        
        # for delays:
        self.delay = str(delay)
    
    
    def commonMixedDerivativeAlternative(self, increment, strideList):
# Способ генерирования кода для смешанной производной для CentralFunction и иногда для граничных функций
        length = len(strideList)
        if length == 2:
            first = 'source['+self.delay+'][idx + (' + strideList[0] + ' + ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            second = ' - source['+self.delay+'][idx - (' + strideList[0] + ' - ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            third = ' - source['+self.delay+'][idx + (' + strideList[0] + ' - ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            fourth = ' + source['+self.delay+'][idx - (' + strideList[0] + ' + ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            finiteDifference = first + second + third + fourth
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'
        else:
            raise SyntaxError("Order of some mixed partial derivative greater than 2. I don't know how to work with it!")
    
    def specialMixedDerivativeAlternative(self, increment, indepVarIndex):
        '''
        INPUT:
        indepVarIndex --- это индекс независимой переменной в массиве всех таких переменных;
                          это индекс той переменной, производная по которой
                          входит в смешанную производную второго порядка,
                          но не той переменной, для которой написано краевое условие Неймана.
        '''
        if self.derivOrder == 2:
            fullIndepVarValueListR = list([])
            fullIndepVarValueListL = list([])
            
            for k,indepVar in enumerate(self.userIndepVariables):
                if k == indepVarIndex:
                    fullIndepVarValueListR.extend(['(idx' + indepVar.upper() + ' + Block' + str(self.blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ' + 1)'])
                else:
                    fullIndepVarValueListR.extend(['(idx' + indepVar.upper() + ' + Block' + str(self.blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ')'])
            fullIndepVarValueListR.extend(['t'])
            
            for k,indepVar in enumerate(self.userIndepVariables):
                if k == indepVarIndex:
                    fullIndepVarValueListL.extend(['(idx' + indepVar.upper() + ' + Block' + str(self.blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ' - 1)'])
                else:
                    fullIndepVarValueListL.extend(['(idx' + indepVar.upper() + ' + Block' + str(self.blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ')'])
            fullIndepVarValueListL.extend(['t'])
            
            right = generateCodeForMathFunction(self.parsedMathFunction, self.userIndepVariables, fullIndepVarValueListR)
            left = generateCodeForMathFunction(self.parsedMathFunction, self.userIndepVariables, fullIndepVarValueListL)
            if right == left:
                return '0.0'
            else:
                return '(0.5 * ' + increment + ' * ' + '(' + '(' + right + ')' + ' - ' + '(' + left + ')' + ')' + ')'
        else:
            raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
    
    def mixDerivative(self):
        increment = '(1 / pow(2,' + str(self.derivOrder) + '))'
        for i,indepVar in enumerate(self.indepVarList):
            increment = increment + ' * D' + indepVar.upper() + 'M' + self.derivativeOrderList[i]
   
        # indepVar_Order_Stride = list([])
        # for i,indepVar in enumerate(self.indepVarList):
        # tup = tuple((indepVar, self.derivativeOrderList[i],
        #              'Block' + str(self.blockNumber) + 'Stride' + indepVar.upper()))
        # indepVar_Order_Stride.extend([tup])

        strideList = []
        for indepVar in self.indepVarList:
            strideList.append('Block' + str(self.blockNumber) + 'Stride' + indepVar.upper())
            
        bCond1 = self.side == 0 or self.side == 1
        bCond2 = self.side == 2 or self.side == 3
        bCond3 = self.side == 4 or self.side == 5
        indepVarCond1 = ((self.indepVarList[0] == self.userIndepVariables[0]
                          and self.indepVarList[1] == self.userIndepVariables[1])
                         or (self.indepVarList[1] == self.userIndepVariables[0]
                             and self.indepVarList[0] == self.userIndepVariables[1]))
        blockDimension = len(self.userIndepVariables)
        if blockDimension > 2:
            indepVarCond2 = ((self.indepVarList[0] == self.userIndepVariables[0]
                              and self.indepVarList[1] == self.userIndepVariables[2])
                             or (self.indepVarList[1] == self.userIndepVariables[0]
                                 and self.indepVarList[0] == self.userIndepVariables[2]))
            indepVarCond3 = ((self.indepVarList[0] == self.userIndepVariables[1]
                              and self.indepVarList[1] == self.userIndepVariables[2])
                             or (self.indepVarList[1] == self.userIndepVariables[1]
                                 and self.indepVarList[0] == self.userIndepVariables[2]))
        
        if ((bCond1 and indepVarCond1)
            or (blockDimension > 2 and bCond3 and indepVarCond3)):
            ind = self.indepVarList.index(self.userIndepVariables[1])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 1)
        elif ((blockDimension > 2 and bCond1 and indepVarCond2)
              or (blockDimension > 2 and bCond2 and indepVarCond3)):
            ind = self.indepVarList.index(self.userIndepVariables[2])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 2)
        elif (bCond2 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond2):
            ind = self.indepVarList.index(self.userIndepVariables[0])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 0)
        else:
            return self.commonMixedDerivativeAlternative(increment, strideList)
