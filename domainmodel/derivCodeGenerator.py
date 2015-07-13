# -*- coding: utf-8 -*-
from someFuncs import NewtonBinomCoefficient, generateCodeForMathFunction

class PureDerivGenerator:
    def __init__(self, blockNumber, unknownVarIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex, secondIndexSTR):
        self.blockNumber = blockNumber
        self.unknownVarIndex = unknownVarIndex
        self.indepVarList = indepVarList
        self.indepVarIndexList = indepVarIndexList
        
        self.derivOrder = 0
        for order in derivativeOrderList:
            self.derivOrder += int(order)
        
        self.userIndepVariables = userIndepVariables
        self.parsedMathFunction = parsedMathFunction
        self.side = side
        self.firstIndex=  firstIndex
        self.secondIndexSTR = secondIndexSTR
    
    def createIndicesList(self):
# Т.к. для CentralFunction умеем генерировать аппроксимации производных любого порядка, то эти аппроксимации содержат много
# слагаемых, каждое из которых имеет свой индекс
        leftIndex = self.derivOrder // 2
        rightIndex = -(self.derivOrder - leftIndex)
        reverseList = [i for i in range(rightIndex,leftIndex + 1)]
        comfortableList = reverseList[::-1]
        indicesListAsString = []
        for index in comfortableList:
            if index >= 0:
                indicesListAsString.extend([' + ' + str(int(index))])
            else:
                indicesListAsString.extend([str(int(index))])
        return indicesListAsString
    
    def createCoefficientList(self):
# Т.к. для CentralFunction умеем генерировать аппроксимации производных любого порядка, то эти аппроксимации содержат много
# слагаемых, перед каждым из которых имеется свой коэффициент
        numberList = [NewtonBinomCoefficient(self.derivOrder, k) for k in range(0, self.derivOrder + 1)]
        stringList = []
        for number in numberList:
            stringList.extend([str(number)])
        return stringList
    
    def pureDerivative(self):
        increment = 'D' + self.indepVarList[0].upper() + 'M' + str(self.derivOrder)
        specialIncrement = 'D' + self.indepVarList[0].upper()
        stride = 'Block' + str(self.blockNumber) + 'Stride' + self.indepVarList[0].upper()
        #Случай соединения блоков
        if self.firstIndex >= 0:
            if self.side / 2 == self.indepVarIndexList[0]:
                return self.interconnectPureDerivAlternative(increment, stride)
            else:
                return self.commonPureDerivativeAlternative(increment, stride)
        #Случай отдельного блока
        else:
            if self.side % 2 == 0 and self.indepVarIndexList[0] == self.side / 2:
                return self.specialPureDerivativeAlternative(increment, specialIncrement, stride, 1)
            elif (self.side - 1) % 2 == 0 and self.indepVarIndexList[0] == (self.side - 1) / 2:
                return self.specialPureDerivativeAlternative(increment, specialIncrement, stride, 0)
            else:
                return self.commonPureDerivativeAlternative(increment, stride)   

    def commonPureDerivativeAlternative(self, increment, stride):
        if self.derivOrder == 1:
            toLeft = 'source[idx - ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            toRight = 'source[idx + ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            return '0.5 * ' + increment + ' * ' + '(' + toRight + ' - ' + toLeft + ')'
        else:
            indicesList = self.createIndicesList()
            coefficientList = self.createCoefficientList()
            finiteDifference = ''
            for i,index in enumerate(indicesList):
                m1 = i % 2
                m2 = (i + 1) % 2
                m3 = i > 0
                m4 = coefficientList[i] != '1.0'
                startOfLine = finiteDifference + m1 * ' - ' + m2 * m3 * ' + ' + m4 * (str(coefficientList[i]) + ' * ')
                restOfLine = 'source[idx' + str(index) + ' * ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
                finiteDifference = startOfLine + restOfLine
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'

    def specialPureDerivativeAlternative(self, increment, specialIncrement, stride, leftOrRightBoundary):
        #leftOrRightBoundary --- это число либо 0 (если краевое условие наложено на левую границу) либо 1 (если краевое условие наложено на правую границу)
        fullIndepVarValueList = list([])
        for indepVar in self.userIndepVariables:
            fullIndepVarValueList.extend(['(idx' + indepVar.upper() + ' + Block' + str(self.blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ')'])
        fullIndepVarValueList.extend(['t'])

        boundaryValue = generateCodeForMathFunction(self.parsedMathFunction, self.userIndepVariables, fullIndepVarValueList)
        if self.derivOrder == 1:
            return boundaryValue
        elif self.derivOrder == 2:
            second = 'source[idx + ' + str(self.unknownVarIndex) + ']'
            m1 = leftOrRightBoundary % 2
            m2 = (leftOrRightBoundary - 1) % 2
            first = 'source[idx' + m1 * ' + ' + m2 * ' - ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            return '(2.0 * '+increment+' * '+'('+first+' - '+second+ m1 * ' - ' + m2 * ' + ' + '(' + boundaryValue + ') * ' + specialIncrement + '))'
        else:
            raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
    
    def interconnectPureDerivAlternative(self, increment, stride):
        if self.side % 2 == 0:
            first = 'source[idx + ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            second = 'ic['+str(self.firstIndex)+'][' + self.secondIndexSTR + ' + ' + str(self.unknownVarIndex) + ']'
        else:
            first = 'ic['+str(self.firstIndex)+'][' + self.secondIndexSTR + ' + ' + str(self.unknownVarIndex) + ']'
            second = 'source[idx - ' + stride + ' * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
        if self.derivOrder == 1:
            return '0.5 * ' + increment + ' * ' + '(' + first + ' - ' + second + ')'
        elif self.derivOrder == 2:
            third = '2.0 * source[idx + ' + str(self.unknownVarIndex) + ']'
            return '(' + increment + ' * ' + '(' + first + ' - ' + third + ' + ' + second + ')' + ')'
        else:
            raise AttributeError("Pure derivative in some equation has order greater than 2!")
    
class MixDerivGenerator:
    def __init__(self, blockNumber, unknownVarIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex, secondIndexSTR):
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
    
    def commonMixedDerivativeAlternative(self, increment, strideList):
# Способ генерирования кода для смешанной производной для CentralFunction и иногда для граничных функций
        length = len(strideList)
        if length == 2:
            first = 'source[idx + (' + strideList[0] + ' + ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            second = ' - source[idx - (' + strideList[0] + ' - ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            third = ' - source[idx + (' + strideList[0] + ' - ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            fourth = ' + source[idx - (' + strideList[0] + ' + ' + strideList[1] + ') * ' + 'Block' + str(self.blockNumber) + 'CELLSIZE + ' + str(self.unknownVarIndex) + ']'
            finiteDifference = first + second + third + fourth
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'
        else:
            raise SyntaxError("Order of some mixed partial derivative greater than 2. I don't know how to work with it!")
    
    def specialMixedDerivativeAlternative(self, increment, indepVarIndex):
#         indepVarIndex --- это индекс независимой переменной в массиве всех таких переменных; это индекс той переменной, производная по которой
#         входит в смешанную производную второго порядка, но не той переменной, для которой написано краевое условие Неймана.
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
#         indepVar_Order_Stride = list([])
#         for i,indepVar in enumerate(self.indepVarList):
#             tup = tuple((indepVar, self.derivativeOrderList[i], 'Block' + str(self.blockNumber) + 'Stride' + indepVar.upper()))
#             indepVar_Order_Stride.extend([tup])
        strideList = []
        for indepVar in self.indepVarList:
            strideList.append('Block' + str(self.blockNumber) + 'Stride' + indepVar.upper())
            
        bCond1 = self.side == 0 or self.side == 1
        bCond2 = self.side == 2 or self.side == 3
        bCond3 = self.side == 4 or self.side == 5
        indepVarCond1 = (self.indepVarList[0] == self.userIndepVariables[0] and self.indepVarList[1] == self.userIndepVariables[1]) or (self.indepVarList[1] == self.userIndepVariables[0] and self.indepVarList[0] == self.userIndepVariables[1])
        blockDimension = len(self.userIndepVariables)
        if blockDimension > 2:
            indepVarCond2 = (self.indepVarList[0] == self.userIndepVariables[0] and self.indepVarList[1] == self.userIndepVariables[2]) or (self.indepVarList[1] == self.userIndepVariables[0] and self.indepVarList[0] == self.userIndepVariables[2])
            indepVarCond3 = (self.indepVarList[0] == self.userIndepVariables[1] and self.indepVarList[1] == self.userIndepVariables[2]) or (self.indepVarList[1] == self.userIndepVariables[1] and self.indepVarList[0] == self.userIndepVariables[2])
        
        if (bCond1 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond3):
            ind = self.indepVarList.index(self.userIndepVariables[1])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 1)
        elif (blockDimension > 2 and bCond1 and indepVarCond2) or (blockDimension > 2 and bCond2 and indepVarCond3):
            ind = self.indepVarList.index(self.userIndepVariables[2])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 2)
        elif (bCond2 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond2):
            ind = self.indepVarList.index(self.userIndepVariables[0])
            specialIncrement = 'D' + self.indepVarList[ind].upper() + 'M' + self.derivativeOrderList[ind]
            return self.specialMixedDerivativeAlternative(specialIncrement, 0)
        else:
            return self.commonMixedDerivativeAlternative(increment, strideList)  
        