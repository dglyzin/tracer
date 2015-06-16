# -*- coding: utf-8 -*-
import numpy as np
import itertools
import re
from equationParser import MathExpressionParser
# from Cheetah.Tests.CheetahWrapper import OUTPUT

class BoundaryFunctionCodeGenerator:
# Генерирует код функции, являющейся краевым условием    
    def __generateCodeForPower(self, preventElementInParsedExpression, creatingOutputList, expressionWithPower):
        power = int(expressionWithPower[1])
        if power > 0:
            if preventElementInParsedExpression != ')':
                expressionToPower = creatingOutputList.pop()
                poweredExpression = expressionToPower
                for i in np.arange(1,power):
                    poweredExpression = poweredExpression + ' * ' + expressionToPower
            else:
                expressionToPower = list([creatingOutputList.pop()])
                count = 1
                while count != 0:
                    helpStr = creatingOutputList.pop()
                    if helpStr == ')':
                        count = count + 1
                    elif helpStr == '(':
                        count = count - 1
                    expressionToPower.extend([helpStr])
#             reverse expression and convert it to string
                expressionToPower = ''.join(expressionToPower[::-1])
                poweredExpression = expressionToPower
                for i in np.arange(1,power):
                    poweredExpression = poweredExpression + ' * ' + expressionToPower
            creatingOutputList.extend([poweredExpression])
        else:
            raise SyntaxError('Power should be greater than zero!')
    
    def __generateDerivative(self, outputList, blockNumber, parsedDrivativeExpression, varIndex, userIndepVariables, tupleList):
# Эта функция должна правильно определить параметры для передачи их в функцию generateCodeForDerivative()
#         Если dictionary пуст, то надо сделать производную для центральной функции
#         Если длина словаря dictionary равна одному, то надо сделать условие на границу отрезка или на сторону прямоугольника или параллелепипеда
#         Если длина словаря dictionary равна двум и длина массива indepVrbls равна двум, то надо сделать условие на угол прямоугольника
#         Если длина словаря dictionary равна двум а длина массива indepVrbls равна трем, то надо сделать условие на ребро
#         Если длина словаря dictionary равна трем, то надо сделать условие на угол параллелепипеда
        dcg = DerivativeCodeGenerator()
        boundaryConditionCount = len(tupleList)
        
        indepVarList = list([])
        indepVarIndexList = list([])
        orderList = list([])
        for i,symbol in enumerate(parsedDrivativeExpression):
            if symbol == '{':
                indepVarList.extend([parsedDrivativeExpression[i+1]])
                indepVarIndexList.extend([userIndepVariables.index(parsedDrivativeExpression[i+1])])
                orderList.extend([parsedDrivativeExpression[i+3]])
        
#         Условие для генерирования производных в центральных функциях
        if boundaryConditionCount == 0:    
            boundaryIndicator = -1
            parsedMathFunction = 'empty string'
            derivative = dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, boundaryIndicator)
#         Условие для обычной границы
        elif boundaryConditionCount == 1:
            boundaryIndicator = tupleList[0][0]
            parsedMathFunction = tupleList[0][1][varIndex]
            derivative = dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, boundaryIndicator)
#         Условие на угол прямоугольника или параллелепипеда или на ребро параллелепипеда        
        elif boundaryConditionCount == 2 or boundaryConditionCount == 3:
            derivativeLR = list([])
            for index in indepVarIndexList:
                if index == tupleList[0][0] // 2:
                    parsedMathFunction = tupleList[0][1][varIndex]
                    boundaryIndicator = tupleList[0][0]                        
                elif index == tupleList[1][0] // 2:
                    parsedMathFunction = tupleList[1][1][varIndex]
                    boundaryIndicator = tupleList[1][0]
                elif boundaryConditionCount == 3 and index == tupleList[2][0] // 2:
                    parsedMathFunction = tupleList[2][1][varIndex]
                    boundaryIndicator = tupleList[2][0]
                else:
                    boundaryIndicator = -1
                    parsedMathFunction = 'empty string'
                derivativeLR.extend([dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, boundaryIndicator)])   
            
            if len(derivativeLR) == 1:
                derivative = derivativeLR[0]
#             Можно написать else, потому что считаем, что производные могут браться максимум второго порядка
            else:
                if derivativeLR[0] != '0.0' and derivativeLR[1] != '0.0':
                    derivative = '(0.5 * ' + derivativeLR[0] + ' + 0.5 * ' + derivativeLR[1] + ')'
                elif derivativeLR[0] == '0.0' and derivativeLR[1] != '0.0':
                    derivative = '(0.5 * ' + derivativeLR[1] + ')'
                elif derivativeLR[0] != '0.0' and derivativeLR[1] == '0.0':
                    derivative = '(0.5 * ' + derivativeLR[0] + ')'
                else:
                    derivative = '0.0'
#         Отмечаем случай, когда в знаменателе получился нуль при аппроксимации производной.
        if derivative == '0.0' and outputList[-1] == ' / ':
            raise SyntaxError("An approximation for mixed derivative" + ''.join(parsedDrivativeExpression) + ", that stands in the denominator, was identically equal to zero during the process of generating function for boundary condition!")
        outputList.extend([derivative])
     
    def generateBoundaryValueCode(self, parsedMathFunction, userIndepVariables, independentVariableValueList):
        outputList = list([])
        operatorList = ['+','-','*','/']
          
        for j,expressionList in enumerate(parsedMathFunction):
            if expressionList[0] == '^':
                self.__generateCodeForPower(parsedMathFunction[j-1], outputList, expressionList)
            elif expressionList in operatorList:
                outputList.extend([' ' + expressionList + ' '])
            elif expressionList in userIndepVariables:
                ind = userIndepVariables.index(expressionList)
                outputList.extend(independentVariableValueList[ind])
            else:
                outputList.extend(expressionList)
     
        string = ''.join(outputList)
        return string
    
    def generateRightHandSideCode(self, blockNumber, leftHandSide, rightHandSide, userIndepVariables, vrbls, params, tupleList = list([])):
#         tupleList --- это список, содержащий от 1 до 3 кортежей (Номер границы, РАСПАРСЕННЫЕ граничные условия)
#         rightHandSide -- распарсенная правая часть уравнения, массив строк.
#         Изменил эту функцию, но не изменил функцию, которая ее вызывает!!!!!!!
        varIndex = vrbls.index(leftHandSide)
        result = '\t result[idx + ' + str(varIndex) + '] = '
        outputList = list([result])
        elemFuncsList = ['exp','sin','sinh','cos','tan','tanh','sqrt','log']
        operatorList = ['+','-','*','/']
        
        for j,expressionList in enumerate(rightHandSide):
            if expressionList[0] == 'D[':
                varIndex = vrbls.index(expressionList[1])
                self.__generateDerivative(outputList, blockNumber, expressionList, varIndex, userIndepVariables, tupleList)
            elif expressionList in vrbls:
                varIndex = vrbls.index(expressionList)
                outputList.extend(['source[idx + ' + str(varIndex) + ']'])
            elif expressionList in params:
                parIndex = params.index(expressionList)
                outputList.extend(['params[' + str(parIndex) + ']'])
            elif expressionList in operatorList:
                outputList.extend([' ' + expressionList + ' '])
            elif expressionList[0] == '^':
                self.__generateCodeForPower(rightHandSide[j-1], outputList, expressionList)
            elif expressionList in elemFuncsList:
                outputList.extend([expressionList])
            else:
                outputList.extend([expressionList])
    
        string = ''.join(outputList) + ';\n'
        return string

class DerivativeCodeGenerator:
# Этот класс отвечает за генерирование кода для производных
    def __factorial(self, number):
# Вычисляет факториал
        if number == 0:
            return 1
        elif number < 0:
            raise AttributeError("The number for factorial shouldn't be less then zero!")
        else:
            i = 1
            product = 1
            while i <= number:
                product = product * i
                i = i + 1
            return product
        
    def __NewtonBinomCoefficient(self, n, k):
# Вычисляет биномиальные коэффициенты затем, чтобы потом их использовать как коэффициенты для конечных разностей
        if n < k:
            raise AttributeError("n souldn't be less then k!")
        return self.__factorial(n) / (self.__factorial(k) * self.__factorial(n-k))
                              
    def __createIndicesList(self, derivativeOrder):
# Т.к. для CentralFunction умеем генерировать аппроксимации производных любого порядка, то эти аппроксимации содержат много
# слагаемых, каждое из которых имеет свой индекс
        leftIndex = derivativeOrder // 2
        rightIndex = -(derivativeOrder - leftIndex)
        reverseList = [i for i in range(rightIndex,leftIndex + 1)]
        comfortableList = reverseList[::-1]
        indicesListAsString = []
        for index in comfortableList:
            if index >= 0:
                indicesListAsString.extend([' + ' + str(float(index))])
            else:
                indicesListAsString.extend([str(float(index))])
        return indicesListAsString
    
    def __createCoefficientList(self, derivativeOrder):
# Т.к. для CentralFunction умеем генерировать аппроксимации производных любого порядка, то эти аппроксимации содержат много
# слагаемых, перед каждым из которых имеется свой коэффициент
        numberList = [self.__NewtonBinomCoefficient(derivativeOrder, k) for k in range(0, derivativeOrder + 1)]
        stringList = []
        for number in numberList:
            stringList.extend([str(number)])
        return stringList
    
    def __commonMixedDerivativeAlternative(self, blockNumber, increment, indepVar_Order_Stride_List, varIndex):
# Способ генерирования кода для смешанной производной для CentralFunction и иногда для границных функций
        length = len(indepVar_Order_Stride_List)
        if length == 2:
            first = 'source[idx + (' + indepVar_Order_Stride_List[0][2] + ' + ' + indepVar_Order_Stride_List[1][2] + ') * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            second = ' - source[idx - (' + indepVar_Order_Stride_List[0][2] + ' - ' + indepVar_Order_Stride_List[1][2] + ') * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            third = ' - source[idx + (' + indepVar_Order_Stride_List[0][2] + ' - ' + indepVar_Order_Stride_List[1][2] + ') * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            fourth = ' + source[idx - (' + indepVar_Order_Stride_List[0][2] + ' + ' + indepVar_Order_Stride_List[1][2] + ') * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            finiteDifference = first + second + third + fourth
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'
        else:
            raise SyntaxError("Order of some mixed partial derivative greater than 2. I don't know how to work with it!")
    
    def __specialMixedDerivativeAlternative(self, parsedMathFunction, increment, strideList, generalOrder, fullIndepVarList, indepVarIndex):
#         indepVarIndex --- это индекс независимой переменной в массиве всех таких переменных; это индекс той переменной, производная по которой
#         входит в смешанную производную второго порядка, но не той переменной, для которой написано краевое условие Неймана.
        if indepVarIndex < 0 or indepVarIndex >= len(fullIndepVarList):
            raise AttributeError("Error in argument of function __specialMixedDerivativeAlternative()! 'indepVarIndex' should be a non-negative integer and less than block dimension!")
        if generalOrder == 2:
            fullIndepVarValueListR = list([])
            fullIndepVarValueListL = list([])
            
            for k,indepVar in enumerate(fullIndepVarList):
                if k == indepVarIndex:
                    fullIndepVarValueListR.extend(['(idx' + indepVar.upper() + ' + 1)'])
                else:
                    fullIndepVarValueListR.extend(['idx' + indepVar.upper()])
            fullIndepVarValueListR.extend(['t'])
            
            for k,indepVar in enumerate(fullIndepVarList):
                if k == indepVarIndex:
                    fullIndepVarValueListL.extend(['(idx' + indepVar.upper() + ' - 1)'])
                else:
                    fullIndepVarValueListL.extend(['idx' + indepVar.upper()])
            fullIndepVarValueListL.extend(['t'])
            
            g = BoundaryFunctionCodeGenerator()
            right = g.generateBoundaryValueCode(parsedMathFunction, fullIndepVarList, fullIndepVarValueListR)
            left = g.generateBoundaryValueCode(parsedMathFunction, fullIndepVarList, fullIndepVarValueListL)
            if right == left:
                return '0.0'
            else:
                return '(0.5 * ' + increment + ' * ' + '(' + right + ' - ' + left + ')' + ')'
        else:
            raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
        
    def __commonPureDerivativeAlternative(self, blockNumber, increment, stride, order, varIndex):
        if order == 1:
            toLeft = 'source[idx - ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            toRight = 'source[idx + ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            return '0.5 * ' + increment + ' * ' + '(' + toRight + ' - ' + toLeft + ')'
        else:
            indicesList = self.__createIndicesList(order)
            coefficientList = self.__createCoefficientList(order)
            finiteDifference = ''
            for i,index in enumerate(indicesList):
                m1 = i % 2
                m2 = (i + 1) % 2
                m3 = i > 0
                m4 = coefficientList[i] != '1.0'
                startOfLine = finiteDifference + m1 * ' - ' + m2 * m3 * ' + ' + m4 * (str(coefficientList[i]) + ' * ')
                restOfLine = 'source[idx' + str(index) + ' * ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
                finiteDifference = startOfLine + restOfLine
            return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'

    def __specialPureDerivativeAlternative(self, blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, fullIndepVarList, leftOrRightBoundary):
#         leftOrRightBoundary --- это число либо 0 (если краевое условие наложено на левую границу) либо 1 (если краевое условие наложено на правую границу)
        if leftOrRightBoundary != 0 and leftOrRightBoundary != 1:
            raise AttributeError("Error in argument of function __specialPureDerivativeAlternative()! 'leftOrRightBoundary' should be equal either to 0 or to 1!")
        
        fullIndepVarValueList = list([])
        for indepVar in fullIndepVarList:
            fullIndepVarValueList.extend(['idx' + indepVar.upper()])
        fullIndepVarValueList.extend(['t'])
        
        b = BoundaryFunctionCodeGenerator()
        boundaryValue = b.generateBoundaryValueCode(parsedMathFunction, fullIndepVarList, fullIndepVarValueList)
        if order == 1:
            return boundaryValue
        elif order == 2:
            second = 'source[idx + ' + str(varIndex) + ']'
            m1 = leftOrRightBoundary % 2
            m2 = (leftOrRightBoundary - 1) % 2
            first = 'source[idx' + m1 * ' + ' + m2 * ' - ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            return '(2.0 * '+increment+' * '+'('+first+' - '+second+ m1 * ' - ' + m2 * ' + ' + '(' + boundaryValue + ') * ' + specialIncrement + '))'
        else:
            raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
    
    def generateCodeForDerivative(self, blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, boundaryIndicator):
        strideList = list([])
        for indepVar in userIndepVariables:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        if len(indepVarList) == 1 or indepVarList[0] == indepVarList[1]: 
            generalOrder = 0
            for order in derivativeOrderList:
                generalOrder = generalOrder + int(order)
            increment = 'D' + indepVarList[0].upper() + 'M' + str(generalOrder)
            specialIncrement = 'D' + indepVarList[0].upper()
            stride = 'Block' + str(blockNumber) + 'Stride' + indepVarList[0].upper()
            order = 0
            for o in derivativeOrderList:
                order = order + int(o)
            
            if boundaryIndicator % 2 == 0 and indepVarIndexList[0] == boundaryIndicator / 2:
                return self.__specialPureDerivativeAlternative(blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, userIndepVariables, 1)
            elif (boundaryIndicator - 1) % 2 == 0 and indepVarIndexList[0] == (boundaryIndicator - 1) / 2:
                return self.__specialPureDerivativeAlternative(blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, userIndepVariables, 0)
            else:
                return self.__commonPureDerivativeAlternative(blockNumber, increment, stride, order, varIndex)
        elif len(indepVarList) == 2:
            generalOrder = 0
            for order in derivativeOrderList:
                generalOrder = generalOrder + int(order)
            increment = '(1 / pow(2,' + str(generalOrder) + '))'
            
            for i,indepVar in enumerate(indepVarList):
                increment = increment + ' * D' + indepVar.upper() + 'M' + derivativeOrderList[i]
            
            indepVar_Order_Stride = list([])
            for i,indepVar in enumerate(indepVarList):
                tup = tuple((indepVar, derivativeOrderList[i], 'Block' + str(blockNumber) + 'Stride' + indepVar.upper()))
                indepVar_Order_Stride.extend([tup])
                
            bCond1 = boundaryIndicator == 0 or boundaryIndicator == 1
            bCond2 = boundaryIndicator == 2 or boundaryIndicator == 3
            bCond3 = boundaryIndicator == 4 or boundaryIndicator == 5
            indepVarCond1 = (indepVarList[0] == userIndepVariables[0] and indepVarList[1] == userIndepVariables[1]) or (indepVarList[1] == userIndepVariables[0] and indepVarList[0] == userIndepVariables[1])
            blockDimension = len(userIndepVariables)
            if blockDimension > 2:
                indepVarCond2 = (indepVarList[0] == userIndepVariables[0] and indepVarList[1] == userIndepVariables[2]) or (indepVarList[1] == userIndepVariables[0] and indepVarList[0] == userIndepVariables[2])
                indepVarCond3 = (indepVarList[0] == userIndepVariables[1] and indepVarList[1] == userIndepVariables[2]) or (indepVarList[1] == userIndepVariables[1] and indepVarList[0] == userIndepVariables[2])
            
            if (bCond1 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond3):
                ind = indepVarList.index(userIndepVariables[1])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, userIndepVariables, 1)
            elif (blockDimension > 2 and bCond1 and indepVarCond2) or (blockDimension > 2 and bCond2 and indepVarCond3):
                ind = indepVarList.index(userIndepVariables[2])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, userIndepVariables, 2)
            elif (bCond2 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond2):
                ind = indepVarList.index(userIndepVariables[0])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, userIndepVariables, 0)
            else:
                return self.__commonMixedDerivativeAlternative(blockNumber, increment, indepVar_Order_Stride, varIndex)
        else:
            raise SyntaxError('Mixed partial derivative has very high order (greater then 2)!')
                  
class FunctionCodeGenerator:
# Генерирует выходную строку для записи в файл
    def generateAllDefinitions(self, parameterCount, indepVariables, DList, allBlockOffsetList, allBlockSizeLists, cellsizeList):
# allBlockSizeLists = [[Block0SizeX, Block0SizeY, Block0SizeZ], [Block1SizeX, Block1SizeY, Block1SizeZ]}, ...]
# allBlockOffsetList = [[Block0OffsetX, Block0OffsetY, Block0OffsetZ], [Block1OffsetX, Block1OffsetY, Block1OffsetZ]}, ...]
# cellsizeList= [Block0CELLSIZE, Block1CELLSIZE, ...]
# allStrideLists --- это список strideОВ для каждого блока: [[block0StrideX,block0StrideY,block0StrideZ],[block1StrideX,Y,Z], ...]
# allCountLists --- аналогичный список, только для countОВ
# DList = [DX,DY,DZ]
# D2List = [DX2,DY2,DZ2]
# DM2List = [DXM2,DYM2,DZM2]
#         Требуем, чтобы длины всех массивов были одинаковы
        if len(DList) != len(indepVariables):
            raise AttributeError("A list 'gridStep' should be consist of values for ALL independent variables!")
        a = set({len(allBlockSizeLists), len(cellsizeList), len(allBlockOffsetList)})
        if len(a) != 1:
            raise AttributeError("Number of elements in 'allBlockSizeLists', 'cellsizeList' and 'allBlockOffsetList' should be the same!")
        
        D2List = list([])
        DM1List = list([])
        DM2List = list([])
        for d in DList:
            d2 = d * d
            D2List.append(d2)
            DM1List.append(round(1 / d))
            DM2List.append(round(1 / d2))
        
#         Вычисляем все страйды и каунты    
        allStrideLists = list([])
        allCountLists = list([])
        for blockNumber, blockSizeList in enumerate(allBlockSizeLists):
            strideList = list([])
            countList = list([])
            for (d, sizeForIndepVar) in zip(DList, blockSizeList):
                countList.append(round(sizeForIndepVar / d))
            allCountLists.append(countList)
            for indepVarIndex,count in enumerate(countList):
                if indepVarIndex == 0:
                    strideList.append(1)
                elif indepVarIndex == 1:
                    strideList.append(countList[0])
                else:
                    strideList.append(countList[0] * countList[1])
            allStrideLists.append(strideList)
        
#         Создаем дефайны
        definitions = list()
        for (indepVar, d, d2, dm1, dm2) in zip(indepVariables, DList, D2List, DM1List, DM2List):
            definitions.append('#define D' + indepVar.upper() + ' ' + str(d) + '\n')
            definitions.append('#define D' + indepVar.upper() + '2 ' + str(d2) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M1 ' + str(dm1) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M2 ' + str(dm2) + '\n')
        for blockNumber,(strideList, countList, offsetList, cellsize) in enumerate(zip(allStrideLists, allCountLists, allBlockOffsetList, cellsizeList)):
            definitions.append('\n#define Block' + str(blockNumber) + 'CELLSIZE' + ' ' + str(cellsize) + '\n\n')
            for (indepVar, stride, count, offset) in zip(indepVariables, strideList, countList, offsetList):
                definitions.append('#define Block' + str(blockNumber) + 'Stride' + indepVar.upper() + ' ' + str(stride) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Count' + indepVar.upper() + ' ' + str(count) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Offset' + indepVar.upper() + ' ' + str(offset) + '\n')
        definitions.append("\n#define PAR_COUNT " + str(parameterCount) + "\n\n")

        return ''.join(definitions)
        
    def __determineNameOfBoundary(self, boundaryNumber):
# Эта функция создана исключительно для красоты и понятности вывода. По номеру границы определяет ее уравнение.
        boundaryNames = dict({0 : 'x = 0', 1 : 'x = x_max', 2 : 'y = 0', 3 : 'y = y_max', 4 : 'z = 0', 5 : 'z = z_max'})
        if boundaryNumber in boundaryNames:
            return boundaryNames[boundaryNumber]
        else:
            raise AttributeError("Error in function __determineNameOfBoundary(): argument 'boundaryNumber' should take only integer values from 0 to 5!")
    
    def __generateFunctionSignature(self, blockNumber, name, indepVariableList, strideList):
#         signature = 'void ' + name + '(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){\n'
#         strBlockNumber = str(blockNumber)
#         idx = "\tint idx = (idxZ*Block" + strBlockNumber + "StrideZ*Block" + strBlockNumber + "StrideY + idxY*Block" + strBlockNumber + "StrideY + idxX)*Block" + strBlockNumber + "CELLSIZE;\n"
        signatureStart = 'void ' + name + '(double* result, double* source, double t,'
        signatureMiddle = ' int idx' + indepVariableList[0].upper() + ','
#         Делаем срез нулевого элемента, т.к. его уже учли
        for indepVar in indepVariableList[1:]:
            signatureMiddle = signatureMiddle + ' int idx' + indepVar.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'
        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ( idx' + indepVariableList[0].upper()
#         Опять срезаем нулевой элемент, т.к. его тоже уже учли
        changedStrideList = strideList[1:]
        for i,indepVar in enumerate(indepVariableList[1:]):
            idx = idx + ' + idx' + indepVar.upper() + ' * ' + changedStrideList[i]
        idx = idx + ') * Block' + str(blockNumber) + 'CELLSIZE;\n'
        
        return list([signature,idx])
    
    def generateCentralFunctionCode(self, block, blockNumber, estrList, defaultIndepVariables, userIndepVariables, params):
#         defaultIndepVrbls отличается лишь количеством элементов userIndepVariables, т.к. считаем, что переменные могут называться только x,y,z.
        function = list([])
        function.extend(['\n//=========================CENTRAL FUNCTION FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
        strideList = list([])
#         Здесь используется defaultIndepVrbls, потому что договорились генерировать сигнатуры функций с одинаковым количеством параметров.
        for indepVar in defaultIndepVariables:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function.extend(['//Central function for '+str(len(userIndepVariables))+'d model for block with number ' + str(blockNumber) + '\n'])    
        function.extend(self.__generateFunctionSignature(blockNumber, 'Block' + str(blockNumber) + 'CentralFunction', defaultIndepVariables, strideList))
            
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        
#         Во все парсеры необходимо передавать именно userIndepVariables!
        b = BoundaryFunctionCodeGenerator()    
        for i,equationString in enumerate(estrList):
            equationRightHandSide = parser.parseMathExpression(equationString, variables, params, userIndepVariables)
            function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equationRightHandSide, userIndepVariables, variables, params)])
        function.extend(['}\n'])
        
        return ''.join(function) + '\n'
    
    def __generateDirichlet(self, blockNumber, name, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionList):
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in defaultIndepVariables:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function = self.__generateFunctionSignature(blockNumber, name, defaultIndepVariables, strideList)
#         А здесь используем userIndepVariables.        
        indepVarValueList = list([])
        for indepVar in userIndepVariables:
            indepVarValueList.extend(['idx' + indepVar.upper()])
        indepVarValueList.extend(['t'])
        
        b = BoundaryFunctionCodeGenerator()
        if len(parsedBoundaryConditionList) > 1:
#             Хотя это бред, потому что я хочу использовать эту функцию для генерирования условий на углы и ребра
            raise AttributeError("Error in function __generateDirichlet(): argument 'parsedBoundaryConditionList' should contain only 1 element!")
        for i,boundary in enumerate(parsedBoundaryConditionList[0][1]):
            boundaryExpression = b.generateBoundaryValueCode(boundary, userIndepVariables, indepVarValueList)
            result = '\t result[idx + ' + str(i) + '] = ' + boundaryExpression + ';\n'
            function.extend([result])
        function.extend(['}\n'])
        
        return ''.join(function)
        
    def __generateNeumann(self, blockNumber, name, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionList): 
#         parsedBoundaryConditionList --- это список, содержащий от 1 до 3 кортежей (Номер границы, РАСПАРСЕННЫЕ граничные условия)
#         parsedEstrList --- список, элементы которого --- распарсенные правые части всех уравнений
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in defaultIndepVariables:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        
        function = self.__generateFunctionSignature(blockNumber, name, defaultIndepVariables, strideList)
        
#         А здесь используем userIndepVariables.
        b = BoundaryFunctionCodeGenerator()
        for i,equation in enumerate(parsedEstrList):
            function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equation, userIndepVariables, variables, params, parsedBoundaryConditionList)])
        function.extend(['}\n'])
        
        return ''.join(function)
    
    def __rectVertexNearSegment(self, ribCoordinateMin, ribCoordinateMax, rectCoordinateList):
# Определяет, лежит ли часть стороны прямоугольника на отрезке. Возвращает 0, если не лежит,
# 1, если лежит не полностью, 2, если лежит полностью.
# rectCoordinateList содержит четыре координаты -- углы прямоугольника
        coord0 = list(rectCoordinateList[0])
        coord1 = list(rectCoordinateList[1])
        coord2 = list(rectCoordinateList[2])
        coord3 = list(rectCoordinateList[3])
        reducedRibCoordinateMin = list(ribCoordinateMin)
        reducedRibCoordinateMax = list(ribCoordinateMax)
        reducedRectCoordList = list([coord0, coord1, coord2, coord3])
        
#         Так как прямоугольник и ребро лежат в одной плоскости, параллельной одной из координатных плоскостей,
#         то одна компонента у всех точек одинаковая, поэтому сводим ситуацию к двумерной, удаляя одинаковую компоненту
        for i in range(0,3):
            if coord0[i] == coord1[i] == coord2[i] == coord3[i]:
                for coordinate in reducedRectCoordList:
                    coordinate.pop(i)
                reducedRibCoordinateMin.pop(i)
                reducedRibCoordinateMax.pop(i)
                break
#         У координат ребра только одна компонента различна, ее и ищем
        index = 0
        for i in range(0,2):
            if reducedRibCoordinateMin[i] != reducedRibCoordinateMax[i]:
                index = i
#         Считаем количество углов прямоугольника, принадлежащих ребру
#         countOfGoodPoints = 0
        goodPoints = list()
        differentCoord = list()
        for (reducedCoord, originalCoord) in zip(reducedRectCoordList, rectCoordinateList):
            left = (reducedCoord[0] - reducedRibCoordinateMax[0]) * (reducedRibCoordinateMin[1] - reducedRibCoordinateMax[1])
            right = (reducedCoord[1] - reducedRibCoordinateMax[1]) * (reducedRibCoordinateMin[0] - reducedRibCoordinateMax[0])
            if left == right and reducedCoord[index] <= reducedRibCoordinateMax[index] and reducedCoord[index] >= reducedRibCoordinateMin[index]:
                goodPoints.extend([originalCoord])
                differentCoord.extend([reducedCoord[index]])
#                 countOfGoodPoints = countOfGoodPoints + 1
        
        return tuple((goodPoints, differentCoord))
    
    def __segmentsIntersects(self, segment1, segment2):
#         segment1, segment2 --- одномерные отрезки, вовсе необязательно, что segmentI[0] <= segmentI[1], I = 1,2!
#         Делаем так, чтобы в обоих отрезках левая граница была <= правой
        if len(segment1) != 2 or len(segment2) != 2:
            raise AttributeError("Lists 'segment1' and 'segment2' in __segmentIntersections() should contain exactly two elements!")
        if segment1[0] > segment1[1]:
            segment1.reverse()
        if segment2[0] > segment2[1]:
            segment2.reverse()
        first = segment1[0] >= segment2[0] and segment1[0] <= segment2[1]
        second = segment1[1] >= segment2[0] and segment1[1] <= segment2[1]
        third = segment2[1] >= segment1[0] and segment2[1] <= segment1[1]
        fourth = segment2[0] >= segment1[0] and segment2[0] <= segment1[1]
        if first or second or third or fourth:
            return True
        else:
            return False
    
    def __determineAllPairsOfConditions(self, resultCondList1, resultCondList2, defaultBoundaryConditions):
#         Для каждого из условий в resultCondList1 ищет все условия из resultCondList2
        outputConditionList = list()
        for boundaryCond1 in resultCondList1:
#             Это список отрезков, пересекающихся с отрезком для boundaryCond1. Друг с другом они не пересекаются,
#             поэтому их можно упорядочить по левой границе.
            listOfSegments = list()
#             Может получится так, что в resultCondList1 лежит хотя бы одно краевое условие,
#             а в resultCondList2 ничего нет. Тогда надо сгенерить пару с дефолтным краевым условием.
            if len(resultCondList2) > 0:
                for boundaryCond2 in resultCondList2:
                    if self.__segmentsIntersects(boundaryCond1[3], boundaryCond2[3]):
                        listOfSegments.extend([boundaryCond2[3]])
                        outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (boundaryCond2[0],boundaryCond2[4]))])
    #                 Сортируем массив отрезков по левой границе
                    listOfSegments.sort(key = lambda lst : lst[0])
                    length = len(listOfSegments)
    #                 Идем по всему списку отрезков и если есть хотя бы 2 не касающихся отрезка,
    #                 то составляем пару (граничное условие, дефолтное граничное условие)
                    if length > 0:
                        if listOfSegments[0][0] <= boundaryCond1[3][0] and listOfSegments[length - 1][1] >= boundaryCond1[3][1]:
                            for i,segment in enumerate(listOfSegments):
                                if i < length - 1 and segment[1] < listOfSegments[i+1][0]:
                                    outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
                                    break
                        else:
                            outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
                    else:
                        outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
            else:
                outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
        return outputConditionList
    
    def __algorithForRib(self, ribCoordinateMin, ribCoordinateMax, boundary1CondList, boundary2CondList, defaultBoundaryConditions):
# Функция возвращает список кортежей --- пар условий.
# ribCoordinateMin = (x,y,z_min), ribCoordinateMax = (x,y,z_max) или x_min x_max или y_min y_max
# Каждый из списков имеет вид [(распарсенное условие 1, [4 координаты углов части 1 границы], Тип условия),
#                              (распарсенное условие 2, [4 координаты углов части 2 границы], Тип условия), ...]
#         Шаг 1: определить все условия, смежные с ребром, на каждой из границ
        result1CondList = list()
        result2CondList = list()
#         Для каждого из списков boundary1CondList и boundary2CondList создали списки условий, котрые смежны с ребром
        generalResultCondList = list([result1CondList, result2CondList])
        
        generalCondList = list([boundary1CondList, boundary2CondList])
        for (boundaryCondList, resultCondList) in zip(generalCondList, generalResultCondList):
            for boundaryCondition in boundaryCondList:
                pointsOnRib = self.__rectVertexNearSegment(ribCoordinateMin, ribCoordinateMax, boundaryCondition[1])
                if len(pointsOnRib[0]) == 2:
#                     (Сами условия, координаты углов, список координат углов на ребре, координаты одномерного отрезка, Тип условия)
                    resultCondList.extend([(boundaryCondition[0], boundaryCondition[1], pointsOnRib[0], pointsOnRib[1], boundaryCondition[2])])
        
#         Шаг 2: теперь составляем всевозможные пары условий (Условие на 1 границу, условие на 2 границу):
#         для каждого условия первой границы берем все подходящие условия второй, и наоборот.
#         Потом их объединяем и возвращаем в виде списка.
        finalResultCondList1 = self.__determineAllPairsOfConditions(generalResultCondList[0], generalResultCondList[1], defaultBoundaryConditions)
        finalResultCondList2 = self.__determineAllPairsOfConditions(generalResultCondList[1], generalResultCondList[0], defaultBoundaryConditions)
#         Надо, чтобы первым элементом кортежа было условие из generalResultCondList[0], поэтому переворачиваем кортежи в finalResultCondList2
        for idx,pair in enumerate(finalResultCondList2):
            tmp = list(finalResultCondList2.pop(idx))
            tmp.reverse()
            finalResultCondList2.insert(idx, tuple(tmp))
#         Исключаем из второго списка все пары, которые уже присутствуют в первом списке.
        for pairTuple in finalResultCondList1:
            if pairTuple in finalResultCondList2:
                finalResultCondList1.remove(pairTuple)
        a = finalResultCondList1 + finalResultCondList2
        return a
    
    def __createBoundaryCoordinates(self, xyzList):
#         Функция по списку xyzList формирует в двумерном случае 2 точки границы, в 3 мерном случае -- 4 точки прямоугольника.
#         xyzList --- список вида [[xFrom, xTo],[yFrom, yTo],[zFrom, zTo]]
        length = len(xyzList)
        if length == 1:
            return xyzList[0]
        elif length >= 2:
            coordinates = []
#             Декартово произведение двух списков. В результате -- список кортежей!
            for point in itertools.product(*xyzList):
                coordinates.append(point)
#             Таким образом устраняем лишние кортежи
            return list(set(coordinates))
        else:
            raise AttributeError("В задаче присутствует более чем 3 независимых переменных!")
                    
    def __generateVertexAndRibFunctions(self, blockNumber, arrWithFunctionNames, blockRanges, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionDictionary):
#         blockRanges --- это словарь {'min' : [x_min,y_min,z_min], 'max' : [x_max,y_max,z_max]}
#         parsedBoundaryConditionDictionary --- это словарь вида {Номер границы : [(распарсенное условие 1, [4 или 2 координаты краев части 1 границы], Тип условия),
#                                                                                  (распарсенное условие 2, [4 или 2 координаты краев части 2 границы], Тип условия), ...]}
#         В двумерном случае [координаты краев части 1 границы] содержат две точки, а в трехмерном --- четыре
        output = list([])
        
        defuaultBoundaryConditionValues = list([])
        for var in variables:
            defuaultBoundaryConditionValues.extend(['0.0'])
        
        blockDimension = len(userIndepVariables)
#         Двумерный случай
        if blockDimension == 2:
            Vertexs = [(0,2),(1,2),(0,3),(1,3)]
            VertexsCoordinates = [(blockRanges['min'][0], blockRanges['min'][1]),(blockRanges['max'][0], blockRanges['min'][1]),
                                  (blockRanges['min'][0], blockRanges['max'][1]),(blockRanges['max'][0], blockRanges['max'][1])]
#             Для каждого угла ищутся граничные условия, заданные пользователем. Если находятся, то используются они,
#             а иначе используются дефолтные
            for i,Vertex in enumerate(Vertexs):
                index = i + 1
#                 if Vertex == (0,2):
#                     index = 1
#                 elif Vertex == (1,2):
#                     index = 2
#                 elif Vertex == (0,3):
#                     index = 3
#                 elif Vertex == (1,3):
#                     index = 4
#                 Делается преобразование в множество потому, что для множеств определена операция isdisjoint()
                c = set([VertexsCoordinates[i]])
                
                bound1CondValue = defuaultBoundaryConditionValues
                bound2CondValue = defuaultBoundaryConditionValues
                type1 = 1
                type2 = 1
                
                if Vertex[0] in parsedBoundaryConditionDictionary:
                    bound1CondList = parsedBoundaryConditionDictionary[Vertex[0]]
                    for boundCondition in bound1CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound1CondValue = boundCondition[0]
#                             Запоминаем типы условий, чтобы потом генерировать либо Дирихле либо Неймана!
                            type1 = boundCondition[2]
                            if type1 != 0 and type1 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if Vertex[1] in parsedBoundaryConditionDictionary:
                    bound2CondList = parsedBoundaryConditionDictionary[Vertex[1]]
                    for boundCondition in bound2CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound2CondValue = boundCondition[0]
                            type2 = boundCondition[2]
                            if type2 != 0 and type2 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                
                boundaryName1 = self.__determineNameOfBoundary(Vertex[0])
                boundaryName2 = self.__determineNameOfBoundary(Vertex[1])
                if bound1CondValue == defuaultBoundaryConditionValues and bound2CondValue == defuaultBoundaryConditionValues:
#                     Генерируется функция для угла по-умолчанию; ничего в массив не записывается, т.к. дефолтное значение уже записано
                    output.extend(['//Default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                    continue
                output.extend(['//Non-default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                if type1 == type2 == 1:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                
                arrWithFunctionNames.pop(index)
                arrWithFunctionNames.insert(index, nameForVertex)
        
#         А в трехмерном случае пока что не учтен массив arrWithFunctionNames       
        elif blockDimension == 3:
            ribs = [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)]
            ribsCoordinates = [[(blockRanges['min'][0], blockRanges['min'][1], blockRanges['min'][2]), (blockRanges['min'][0], blockRanges['min'][1], blockRanges['max'][2])],
                               [(blockRanges['min'][0], blockRanges['max'][1], blockRanges['min'][2]), (blockRanges['min'][0], blockRanges['max'][1], blockRanges['max'][2])],
                               [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['min'][2]), (blockRanges['min'][0], blockRanges['max'][1], blockRanges['min'][2])],
                               [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['max'][2]), (blockRanges['min'][0], blockRanges['max'][1], blockRanges['max'][2])],
                               [(blockRanges['max'][0], blockRanges['min'][1], blockRanges['min'][2]), (blockRanges['max'][0], blockRanges['min'][1], blockRanges['max'][2])],
                               [(blockRanges['max'][0], blockRanges['max'][1], blockRanges['min'][2]), (blockRanges['max'][0], blockRanges['max'][1], blockRanges['max'][2])],
                               [(blockRanges['max'][0], blockRanges['min'][1], blockRanges['min'][2]), (blockRanges['max'][0], blockRanges['max'][1], blockRanges['min'][2])],
                               [(blockRanges['max'][0], blockRanges['min'][1], blockRanges['max'][2]), (blockRanges['max'][0], blockRanges['max'][1], blockRanges['max'][2])],
                               [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['min'][2]), (blockRanges['max'][0], blockRanges['min'][1], blockRanges['min'][2])],
                               [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['max'][2]), (blockRanges['max'][0], blockRanges['min'][1], blockRanges['max'][2])],
                               [(blockRanges['min'][0], blockRanges['max'][1], blockRanges['min'][2]), (blockRanges['max'][0], blockRanges['max'][1], blockRanges['min'][2])],
                               [(blockRanges['min'][0], blockRanges['max'][1], blockRanges['max'][2]), (blockRanges['max'][0], blockRanges['max'][1], blockRanges['max'][2])]]
            for idx,rib in enumerate(ribs):
                boundaryName1 = self.__determineNameOfBoundary(rib[0])
                boundaryName2 = self.__determineNameOfBoundary(rib[1])
                pairsOfBoundaryCondition = list()
                if rib[0] in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                    boundary1CondList = parsedBoundaryConditionDictionary[rib[0]]
                    boundary2CondList = parsedBoundaryConditionDictionary[rib[1]]
                    pairsOfBoundaryCondition = self.__algorithForRib(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundary1CondList, boundary2CondList, defuaultBoundaryConditionValues)
                elif rib[0] in parsedBoundaryConditionDictionary and rib[1] not in parsedBoundaryConditionDictionary:
#                     Здесь надо сначала определить те границы, которые касаются ребра, и для каждой из них
#                     сгенерить функцию
                    for boundaryCondition in parsedBoundaryConditionDictionary[rib[0]]:
                        if len(self.__rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((boundaryCondition[0],boundaryCondition[2]), (defuaultBoundaryConditionValues,1)))
                elif rib[0] not in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                    for boundaryCondition in parsedBoundaryConditionDictionary[rib[1]]:
                        if len(self.__rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((defuaultBoundaryConditionValues,1), (boundaryCondition[0],boundaryCondition[2])))
                else:
                    continue
                for number,pair in enumerate(pairsOfBoundaryCondition):
                    output.extend(['//Non-default boundary condition for RIB between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + ' with number ' + str(number) + '\n'])
                    if pair[0][1] == pair[1][1] == 1:
                        nameForRib = 'Block' + str(blockNumber) + 'NeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0])), tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateNeumann(blockNumber, nameForRib, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                    elif pair[0][1] == 0:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                    else:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
            
            Vertexs = [(0,2,4),(0,2,5),(0,3,4),(0,3,5),(1,2,4),(1,2,5),(1,3,4),(1,3,5)]
            VertexsCoordinates = [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['min'][2]),
                                 (blockRanges['min'][0], blockRanges['min'][1], blockRanges['max'][2]),
                                 (blockRanges['min'][0], blockRanges['max'][1], blockRanges['min'][2]),
                                 (blockRanges['min'][0], blockRanges['max'][1], blockRanges['max'][2]),
                                 (blockRanges['max'][0], blockRanges['min'][1], blockRanges['min'][2]),
                                 (blockRanges['max'][0], blockRanges['min'][1], blockRanges['max'][2]),
                                 (blockRanges['max'][0], blockRanges['max'][1], blockRanges['min'][2]),
                                 (blockRanges['max'][0], blockRanges['max'][1], blockRanges['max'][2])]
            
            for i,Vertex in enumerate(Vertexs):
                c = set([VertexsCoordinates[i]])
                    
                bound1CondValue = defuaultBoundaryConditionValues
                bound2CondValue = defuaultBoundaryConditionValues
                bound3CondValue = defuaultBoundaryConditionValues
                type1 = 1
                type2 = 1
                type3 = 1
                    
                if Vertex[0] in parsedBoundaryConditionDictionary:
                    bound1CondList = parsedBoundaryConditionDictionary[Vertex[0]]
                    for boundCondition in bound1CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound1CondValue = boundCondition[0]
                            type1 = boundCondition[2]
                            if type1 != 0 and type1 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if Vertex[1] in parsedBoundaryConditionDictionary:
                    bound2CondList = parsedBoundaryConditionDictionary[Vertex[1]]
                    for boundCondition in bound2CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound2CondValue = boundCondition[0]
                            type2 = boundCondition[2]
                            if type2 != 0 and type2 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if Vertex[2] in parsedBoundaryConditionDictionary:
                    bound3CondList = parsedBoundaryConditionDictionary[Vertex[2]]
                    for boundCondition in bound3CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound3CondValue = boundCondition[0]
                            type3 = boundCondition[2]
                            if type3 != 0 and type3 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if bound1CondValue == defuaultBoundaryConditionValues and bound2CondValue == defuaultBoundaryConditionValues and bound3CondValue == defuaultBoundaryConditionValues:
                    continue
                
                boundaryName1 = self.__determineNameOfBoundary(Vertex[0])
                boundaryName2 = self.__determineNameOfBoundary(Vertex[1])
                boundaryName3 = self.__determineNameOfBoundary(Vertex[2])
                output.extend(['//Non-default boundary condition for Vertex between boundaries ' + boundaryName1 + ', ' + boundaryName2 + ' and ' + boundaryName3 + '\n'])
                if type1 == type2 == type3 == 1:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue)), tuple((Vertex[2], bound3CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                elif type2 == 0:
                    boundaryConditionList = list([tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((Vertex[2], bound3CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, defaultIndepVariables, userIndepVariables, params, boundaryConditionList)])

        return output
    
#     def generateBoundaryFunctionsCode(self, blockNumber, blockRanges, boundaryConditionList, estrList, defaultIndepVariables, userIndepVariables, params):
# #         includes = '#include <Math.h>\n#include <stdlib.h>\n\n'
# #         boundaryConditionList имеет структуру [{'values':[], 'type':тип, 'side':номер границы, 'ranges':[[xFrom,xTo],[y],[z]]}]
#         outputFile = list(['\n//=============================NON-DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'])
#         parser = MathExpressionParser()
#         variables = parser.getVariableList(estrList)
#         
#         parsedEstrList = list([])
#         for equation in estrList:
#             parsedEstrList.extend([parser.parseMathExpression(equation, variables, params, userIndepVariables)])
#         
#         numberOfVariables = len(variables)
#         for boundaryCondition in boundaryConditionList:
#             if len(boundaryCondition['values']) != numberOfVariables:
#                 raise SyntaxError("The dimension of unknow vector-function is " + str(numberOfVariables) + ", but one of the input boundary conditions has other number of components!")
#         
#         boundaryNumberList = list([])
#         parsedBoundaryConditionDictionary = dict({})
#         boundaryCount = len(userIndepVariables) * 2
# #         Этот словарь будет помогать правильно нумеровать сишные функции
#         countOfGeneratedFunction = dict({})
#         for boundaryCondition in boundaryConditionList:
#             
#             boundaryNumber = boundaryCondition['side']
#             if boundaryNumber in countOfGeneratedFunction:
#                 countOfGeneratedFunction[boundaryNumber] += 1
#             else:
#                 countOfGeneratedFunction.update({boundaryNumber: 0})
#                 
#             coordList = boundaryCondition['ranges']
# #             Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
#             boundaryCoordList = self.__createBoundaryCoordinates(coordList)
#             
#             if boundaryNumber >= boundaryCount:
#                 raise AttributeError("Error in boundary conditions entry: a value for the key 'side' shouldn't be greater than number of block boundaries!")
#             indepVarsForBoundaryFunction = list(userIndepVariables)
#             indepVarsForBoundaryFunction.remove(userIndepVariables[boundaryNumber // 2])
#             indepVarsForBoundaryFunction.extend(['t'])
#             
#             parsedBoundaryCondition = list([])
#             for boundary in boundaryCondition['values']:
#                 parsedBoundaryCondition.extend([parser.parseMathExpression(boundary, params, indepVarsForBoundaryFunction)])
#             parsedBoundaryConditionTuple = list([tuple((boundaryNumber, parsedBoundaryCondition))])
#             
#             if boundaryNumber in parsedBoundaryConditionDictionary:
#                 parsedBoundaryConditionDictionary[boundaryNumber].append((parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type']))
#             else:
#                 boundaryNumberList.extend([boundaryNumber])
#                 parsedBoundaryConditionDictionary.update({boundaryNumber : [(parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type'])]})
#             
#             boundaryName = self.__determineNameOfBoundary(boundaryNumber)
#             dimension = len(userIndepVariables)
#             if dimension >= 1:
#                 xRangeForName = "xfrom = " + str(coordList[0][0]) + ", xto = " + str(coordList[0][1])
#                 rangesForName = xRangeForName
#             if dimension >= 2:
#                 yRangeForName = "yfrom = " + str(coordList[1][0]) + ", yto = " + str(coordList[1][1])
#                 rangesForName = rangesForName + ', ' + yRangeForName
#             if dimension == 3:
#                 zRangeForName = "zfrom = " + str(coordList[2][0]) + ", zto = " + str(coordList[2][1])
#                 rangesForName = rangesForName + ', ' + zRangeForName
#             outputFile.extend(['//Non-default boundary condition for boundary ' + boundaryName + ' with ranges ' + rangesForName + '\n'])
#             if boundaryNumber >= boundaryCount:
#                 raise SyntaxError('An attempt to impose the condition for boundary with non-existent number ' + str(boundaryNumber) + '! Maximal number of boundaies is equal ' + str(boundaryCount) + '!')
#             if boundaryCondition['type'] == 0:
#                 outputFile.extend([self.__generateDirichlet(blockNumber, 'Block' + str(blockNumber) + 'DirichletBound' + str(boundaryNumber) + '_' + str(countOfGeneratedFunction[boundaryNumber]), defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
#             else:
#                 outputFile.extend([self.__generateNeumann(blockNumber, 'Block' + str(blockNumber) + 'NeumannBound' + str(boundaryNumber) + '_' + str(countOfGeneratedFunction[boundaryNumber]), parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
#         
#         outputFile.extend(self.__generateVertexAndRibFunctions(blockNumber, blockRanges, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionDictionary))
#         return ''.join(outputFile)
    
#     def generateDefaultBoundaryFunction(self, block, blockNumber, estrList, defaultIndepVariables, userIndepVariables, params):
#         defaultFunctions = list([])
#         parser = MathExpressionParser()
#         variables = parser.getVariableList(estrList)
#             
#         parsedEstrList = list([])
#         for equation in estrList:
#             parsedEstrList.extend([parser.parseMathExpression(equation, variables, params, userIndepVariables)])
#             
# #         defuaultBoundaryConditionValues = list([])
#         defuaultBoundaryConditionValues = len(variables) * ['0.0']
# #         for var in variables:
# #             defuaultBoundaryConditionValues.extend(['0.0'])
#                 
#         defaultFunctions.extend(['\n//=========================DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
#                 
#         boundaryCount = len(userIndepVariables) * 2
#         for i in range(0,boundaryCount):
#             boundaryName = self.__determineNameOfBoundary(i)
#             defaultFunctions.extend(['//Default boundary condition for boundary ' + boundaryName + '\n'])
#             nameForSide = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(i)
#             defaultBoundaryConditionList = list([tuple((i, defuaultBoundaryConditionValues))])
#             defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForSide, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, defaultBoundaryConditionList)])
#             
#         if len(userIndepVariables) == 2:
#             Vertexs = [(0,2),(0,3),(1,2),(1,3)]
#             for Vertex in Vertexs:
#                 boundaryName1 = self.__determineNameOfBoundary(Vertex[0])
#                 boundaryName2 = self.__determineNameOfBoundary(Vertex[1])
#                 defaultFunctions.extend(['//Default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
#                 defaultBoundaryConditionList = list([tuple((Vertex[0], defuaultBoundaryConditionValues)), tuple((Vertex[1], defuaultBoundaryConditionValues))])
#                 nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
#                 defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, defaultBoundaryConditionList)])
#                     
# #             defaultFunctions.extend([self.__generateVertexOrRib(blockNumber, nameForVertex, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
#         elif len(userIndepVariables) == 3:
#             ribs = [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)]
#             for rib in ribs:
#                 boundaryName1 = self.__determineNameOfBoundary(rib[0])
#                 boundaryName2 = self.__determineNameOfBoundary(rib[1])
#                 defaultFunctions.extend(['//Default boundary condition for rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
#                 defaultBoundaryConditionList = list([tuple((rib[0], defuaultBoundaryConditionValues)), tuple((rib[1], defuaultBoundaryConditionValues))])
#                 nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1])
#                 defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, defaultBoundaryConditionList)])
#             Vertexs = [(0,2,4),(0,2,5),(0,3,4),(0,3,5),(1,2,4),(1,2,5),(1,3,4),(1,3,5)]
#             for Vertex in Vertexs:
#                 boundaryName1 = self.__determineNameOfBoundary(Vertex[0])
#                 boundaryName2 = self.__determineNameOfBoundary(Vertex[1])
#                 boundaryName3 = self.__determineNameOfBoundary(Vertex[2])
#                 defaultFunctions.extend(['//Default boundary condition for Vertex between boundaries ' + boundaryName1 + ', ' + boundaryName2 + ' and ' + boundaryName3 + '\n'])
#                 defaultBoundaryConditionList = list([tuple((Vertex[0], defuaultBoundaryConditionValues)), tuple((Vertex[1], defuaultBoundaryConditionValues)), tuple((Vertex[2], defuaultBoundaryConditionValues))])
#                 nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1]) + '_' + str(Vertex[2])
#                 defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, defaultBoundaryConditionList)])
#         
#         return ''.join(defaultFunctions)
#     


    def __computeSideLength2D(self, blockRanges, Side):
#         blockRanges --- словарь {"min": [x,y,z], "max": [x,y,z]}
#         side --- номер стороны, длину которой надо вычислить       
        if Side == 0 or Side == 1:
            return blockRanges["max"][1] - blockRanges["min"][1]
        elif Side == 2 or Side == 3:
            return blockRanges["max"][0] - blockRanges["min"][0]
        else:
            raise AttributeError("Side should be 0, 1, 2 or 3!")
    
    def __computeSegmentLength2D(self, segment):
#         segment = [(x1,y1),(x2,y2)]
        if len(segment) != 2 or len(segment[0]) != 2 or len(segment[1]) != 2:
            raise AttributeError("List 'segment' in __computeSegmentLength2D() should contain exactly two elements!")
#         т.к. отрезки параллельны осям кординат, то можно делать так
        reducedSegment = []
#         Двумерный случай сводится к одномерному
        if segment[0][0] == segment[1][0]:
            reducedSegment = [min([segment[0][1], segment[1][1]]), max([segment[0][1], segment[1][1]])]
        elif segment[0][1] == segment[1][1]:
            reducedSegment = [min([segment[0][0], segment[1][0]]), max([segment[0][0], segment[1][0]])]
            
        return reducedSegment[1] - reducedSegment[0]
    
    def __generateBoundaryFuncsForBlockInProperOrder(self, blockNumber, arrWithFunctionNames, blockRanges, boundaryConditionList, estrList, defaultIndepVariables, userIndepVariables, params):
        outputFile = list(['\n//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'])
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        
#         Это дефолтные неймановские краевые условия
        defuaultBoundaryConditionValues = list([])
        for var in variables:
            defuaultBoundaryConditionValues.extend(['0.0'])
        
        parsedEstrList = list([])
        for equation in estrList:
            parsedEstrList.extend([parser.parseMathExpression(equation, variables, params, userIndepVariables)])
        
        numberOfVariables = len(variables)
        for boundaryCondition in boundaryConditionList:
            if len(boundaryCondition['values']) != numberOfVariables:
                raise SyntaxError("The dimension of unknow vector-function is " + str(numberOfVariables) + ", but one of the input boundary conditions has other number of components!")
        
        boundaryNumberList = list([])
        parsedBoundaryConditionDictionary = dict({})
        boundaryCount = len(userIndepVariables) * 2
#         Этот словарь будет помогать правильно нумеровать сишные функции
        countOfGeneratedFunction = dict({})
        for boundaryCondition in boundaryConditionList:
            
            side = boundaryCondition['side']
            if side in countOfGeneratedFunction:
                countOfGeneratedFunction[side] += 1
            else:
                countOfGeneratedFunction.update({side: 0})
                
            coordList = boundaryCondition['ranges']
#             Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
            boundaryCoordList = self.__createBoundaryCoordinates(coordList)
            
            if side >= boundaryCount:
                raise AttributeError("Error in boundary conditions entry: a value for the key 'side' shouldn't be greater than number of block boundaries!")
            indepVarsForBoundaryFunction = list(userIndepVariables)
            indepVarsForBoundaryFunction.remove(userIndepVariables[side // 2])
            indepVarsForBoundaryFunction.extend(['t'])
            
            parsedBoundaryCondition = list([])
            for boundary in boundaryCondition['values']:
                parsedBoundaryCondition.extend([parser.parseMathExpression(boundary, params, indepVarsForBoundaryFunction)])
            
            if side in parsedBoundaryConditionDictionary:
                parsedBoundaryConditionDictionary[side].append((parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type']))
            else:
                boundaryNumberList.extend([side])
                parsedBoundaryConditionDictionary.update({side : [(parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type'])]})
        
        dimension = len(userIndepVariables)
        properSequenceOfSides = [2,3,0,1]    
#         for side in range(0, boundaryCount):
        for side in properSequenceOfSides:
            boundaryName = self.__determineNameOfBoundary(side)
            if side in parsedBoundaryConditionDictionary:
                if dimension == 2:
#                 Если нужно, кладем имя граничной функции по умолчанию в массив
                    sideLen = self.__computeSideLength2D(blockRanges, side)
#                 Сумма длин всех отрезков на стороне side, на которые наложены условия
                    totalLen = 0
                    for condition in parsedBoundaryConditionDictionary[side]:
                        totalLen += self.__computeSegmentLength2D(condition[1])
                    if sideLen > totalLen:
                        outputFile.extend(['//Default boundary condition for boundary ' + boundaryName + '\n'])
                        parsedBoundaryConditionTuple = list([tuple((side, defuaultBoundaryConditionValues))])
                        name = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(side)
                        outputFile.extend([self.__generateNeumann(blockNumber, name, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
                        arrWithFunctionNames.append(name)
#                 Генерируем функции для всех заданных условий и кладем их имена в массив
                counter = 0
                for condition in parsedBoundaryConditionDictionary[side]:
                    parsedBoundaryConditionTuple = list([tuple((side, condition[0]))])
                    if dimension == 1 or dimension == 2:
                        outputFile.extend(['//Non-default boundary condition for boundary ' + boundaryName + '\n'])
                        if condition[2] == 0:
                            name = 'Block' + str(blockNumber) + 'DirichletBound' + str(side) + '_' + str(counter)
                            outputFile.extend([self.__generateDirichlet(blockNumber, name, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
                            arrWithFunctionNames.append(name)
                        else:
                            name = 'Block' + str(blockNumber) + 'NeumannBound' + str(side) + '_' + str(counter)
                            outputFile.extend([self.__generateNeumann(blockNumber, name, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
                            arrWithFunctionNames.append(name)
                    elif dimension == 3:
                        raise AttributeError("Three dimensional case!")
                    counter += 1
        
            else:
                outputFile.extend(['//Default boundary condition for boundary ' + boundaryName + '\n'])
                parsedBoundaryConditionTuple = list([tuple((side, defuaultBoundaryConditionValues))])
                name = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(side)
                outputFile.extend([self.__generateNeumann(blockNumber, name, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
                arrWithFunctionNames.append(name)
#             boundaryName = self.__determineNameOfBoundary(side)
#             dimension = len(userIndepVariables)
#             if dimension >= 1:
#                 xRangeForName = "xfrom = " + str(coordList[0][0]) + ", xto = " + str(coordList[0][1])
#                 rangesForName = xRangeForName
#             if dimension >= 2:
#                 yRangeForName = "yfrom = " + str(coordList[1][0]) + ", yto = " + str(coordList[1][1])
#                 rangesForName = rangesForName + ', ' + yRangeForName
#             if dimension == 3:
#                 zRangeForName = "zfrom = " + str(coordList[2][0]) + ", zto = " + str(coordList[2][1])
#                 rangesForName = rangesForName + ', ' + zRangeForName
#             outputFile.extend(['//Non-default boundary condition for boundary ' + boundaryName + ' with ranges ' + rangesForName + '\n'])
#             if side >= boundaryCount:
#                 raise SyntaxError('An attempt to impose the condition for boundary with non-existent number ' + str(side) + '! Maximal number of boundaies is equal ' + str(boundaryCount) + '!')
#             if boundaryCondition['type'] == 0:
#                 outputFile.extend([self.__generateDirichlet(blockNumber, 'Block' + str(blockNumber) + 'DirichletBound' + str(side) + '_' + str(countOfGeneratedFunction[side]), defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
#             else:
#                 outputFile.extend([self.__generateNeumann(blockNumber, 'Block' + str(blockNumber) + 'NeumannBound' + str(side) + '_' + str(countOfGeneratedFunction[side]), parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionTuple)])
        
        outputFile.extend(self.__generateVertexAndRibFunctions(blockNumber, arrWithFunctionNames, blockRanges, parsedEstrList, variables, defaultIndepVariables, userIndepVariables, params, parsedBoundaryConditionDictionary))
        return ''.join(outputFile)
    

    
    def generateAllBoundaries(self, block, blockNumber, arrWithFunctionNames, estrList, bounds, defaultIndepVariables, userIndepVariables, params):
# Эта функция должна для блока block сгенерировать все нужные функции.
# Массив bounds имеет ту же структуру и смысл, что и в классе Model
        boundaryFunctions = list()
        blockDimension = block.dimension
#         Offset -- это смещение блока, Size -- длина границы, поэтому границы блока -- это [Offset, Offset + Size]
        minRanges = [block.offsetX]
        maxRanges = [block.offsetX + block.sizeX]
        if blockDimension >= 2:
            minRanges = minRanges + [block.offsetY]
            maxRanges = maxRanges + [block.offsetY + block.sizeY]
        if blockDimension == 3:
            minRanges = minRanges + [block.offsetZ]
            maxRanges = maxRanges + [block.offsetZ + block.sizeZ]
        blockRanges = dict({'min' : minRanges, 'max' : maxRanges})
#        Надо сформировать структуру boundaryConditionList = [{'values':[], 'type':тип, 'side':номер границы, 'ranges':[[xFrom,xTo],[y],[z]]}]
        boundaryConditionList = list()
        boundRegions = block.boundRegions
        for region in boundRegions:
#             терминология, связанная с boundRegions, неизвестна
            boundNumber = region.boundNumber
            if boundNumber >= len(bounds):
                raise AttributeError("Non-existent number of boundary condition is set for some of boundary regions in array 'Blocks'!")
            side = region.side
            
            if blockDimension == 1:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX]]
                else:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX]]
            elif blockDimension == 2:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX], [region.yfrom, region.yto]]
                elif side == 1:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX], [region.yfrom, region.yto]]
                elif side == 2:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY, block.offsetY]]
                else:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY + block.sizeY, block.offsetY + block.sizeY]]
            else:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
                elif side == 1:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
                elif side == 2:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY, block.offsetY], [region.zfrom, region.zto]]
                elif side == 3:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY + block.sizeY, block.offsetY + block.sizeY], [region.zfrom, region.zto]]
                elif side == 4:
                    boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ, block.offsetZ]]
                elif side == 5:
                    boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ + block.sizeZ, block.offsetZ + block.sizeZ]]

            bound = bounds[boundNumber]
#             Если условие Дирихле, то используем производные по t,
#             если Неймановское условие --- то сами значения.
            boundaryType = bound.btype
            if boundaryType == 0:
                values = bound.derivative
            elif boundaryType == 1:
                values = bound.values
                
            boundaryCondition = dict({'values': values, 'type': boundaryType, 'side': side, 'ranges': boundaryRanges})
            boundaryConditionList.append(boundaryCondition)
#         Теперь надо вызвать функцию, генерирующую граничные условия для данного блока
#         boundaryFunctions.append(self.generateBoundaryFunctionsCode(blockNumber, blockRanges, boundaryConditionList, estrList, defaultIndepVariables, userIndepVariables, params))
        boundaryFunctions.append(self.__generateBoundaryFuncsForBlockInProperOrder(blockNumber, arrWithFunctionNames, blockRanges, boundaryConditionList, estrList, defaultIndepVariables, userIndepVariables, params))
        return ''.join(boundaryFunctions)
    
    def __generateParamFunction(self, params, paramValues):
#         params -- массив имен параметров, paramValues -- словарь значений
        paramCount = len(params)
        paramValuesCount = len(paramValues)
        if paramCount != paramValuesCount:
            raise AttributeError("Count of parameter values is not corresponds to count of parameters!")
        
        output = list(["void initDefaultParams(double** pparams, int* pparamscount){\n"])
        output.append("\t*pparamscount = PAR_COUNT;\n")
        output.append("\t*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);\n")
        
        for index,param in enumerate(params):
            output.append("\t(*pparams)[" + str(index) + "] = " + str(paramValues[param]) + ";\n")
        
        output.append("}\n\nvoid releaseParams(double *params){\n\tfree(params);\n}\n\n")
        
        return ''.join(output)
    
    def __generatePointInitial(self, countOfEquations, initial, initialNumber, indepVariableList):
#         Функция генерируют точечную начальную функцию с номером initialNumber.
#         changedValueList --- будет содержать строки, которые просто надо подставить в нужное место и не надо парсить.
        pointFunction = list()
#         changedValueList = list()
        valueList = initial.values
        if len(valueList) != countOfEquations:
            raise AttributeError("Component's count of some initial condition is not corresponds to component's count of unknown vector-function!")
#         for value in valueList:
#             changedValue = value
#             for i,indepVariable in enumerate(indepVariableList):
#                 if i == 0:
#                     new = 'x'
#                 elif i == 1:
#                     new = 'y'
#                 else:
#                     new = 'z'
#                 changedValue = changedValue.replace(indepVariable, new)
#             changedValueList.append(changedValue)
#         
        pointFunction.append("void Initial"+str(initialNumber)+"(double* cellstart, double x, double y, double z){\n")
        t = re.compile('t')
#         Функция, которая в выражении match.group() заменяет все 't' на '0.0'
        repl = lambda match: t.sub('0.0', match.group())
        for k,value in enumerate(valueList):
#             Т.к. начальные условия не должны зависеть от t, его надо везде заменить на 0
#             newValue = value.replace('t','0.0')
#             Этот вариант замещает не всегда правильно! надо переделать.
            newValue = re.sub('\(.*?\)',repl,value)
            pointFunction.append("\tcellstart[" + str(k) + "] = " + newValue + ";\n")
        pointFunction.append("}\n\n")
        return ''.join(pointFunction)
    
    def __generateFillFunctionForBlock(self, blockNumber, countOfInitials, indepVariableList):
        fillFunction = list()
        strBlockNum = str(blockNumber)
#         otherParameters будут вставляться в строку signature, если это потребуется.
#         otherParameters = ", int Block" + strBlockNum + "CountX, int Block" + strBlockNum + "CountY, int Block" + strBlockNum + "CountZ, int Block" + strBlockNum + "OffsetX, int Block" + strBlockNum + "OffsetY, int Block" + strBlockNum + "OffsetZ"
        signature = "void Block" + strBlockNum + "FillInitialValues(double* result, int* initType){\n"
        fillFunction.append(signature)
        
        fillFunction.append("\tinitfunc_ptr_t initFuncArray[" + str(countOfInitials) + "];\n")
        for i in range(0, countOfInitials):
            index = str(i)
            fillFunction.append("\tinitFuncArray[" + index + "] = Initial" + index + ";\n")
        
#         В зависимости от размерности блока генерируется 1, 2 или 3 цикла for
        dimension = len(indepVariableList)
        if dimension == 3:
            fillFunction.append("\tfor(int idxZ = 0; idxZ<Block" + strBlockNum + "CountZ; idxZ++)\n")
            fillFunction.append("\t\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n")
            fillFunction.append("\t\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
            spaces = "\t\t\t\t"
            idx = "int idx = (idxZ*Block" + strBlockNum + "CountY*Block" + strBlockNum + "CountX + idxY*Block" + strBlockNum + "CountX + idxX)*Block" + strBlockNum + "CELLSIZE;\n"
            params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, Block" + strBlockNum + "OffsetZ + idxZ*DZ"  
        elif dimension == 2:
            fillFunction.append("\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n")
            fillFunction.append("\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
            spaces = "\t\t\t"
            idx = "int idx = (idxY*Block" + strBlockNum + "CountX + idxX)*Block" + strBlockNum + "CELLSIZE;\n"
            params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, 0"
        else:
            fillFunction.append("\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
            spaces = "\t\t"
            idx = "int idx = idxX*Block" + strBlockNum + "CELLSIZE;\n"
            params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, 0, 0"
        fillFunction.append(spaces + idx)
        fillFunction.append(spaces + "int type = initType[idx];\n")
        fillFunction.append(spaces + "initFuncArray[type](" + params + ");}\n")
#         fillFunction.append("\tfor(int idxZ = 0; idxZ<Block" + strBlockNum + "CountZ; idxZ++)\n")
#         fillFunction.append("\t\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n")
#         fillFunction.append("\t\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
#         fillFunction.append("\t\t\t\tint idx = (idxZ*Block" + strBlockNum + "CountY*Block" + strBlockNum + "CountX + idxY*Block" + strBlockNum + "CountX + idxX)*Block" + strBlockNum + "CELLSIZE;\n")
#         fillFunction.append("\t\t\t\tint type = initType[idx];\n")
#         fillFunction.append("\t\t\t\tinitFuncArray[type](result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, Block" + strBlockNum + "OffsetZ + idxZ*DZ);\n\t\t\t}\n")
        
        fillFunction.append("}\n\n")
        
        return ''.join(fillFunction)
    
    def __generateGetInitFuncArray(self, countOfBlocks):
        strCountOfBlocks = str(countOfBlocks)
        output = list(["void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs){\n"])
        output.append('\tprintf("Welcome into userfuncs.so. Getting initial functions...\\n");\n')
        output.append("\tinitfunc_fill_ptr_t* pInitFuncs;\n")
        output.append("\tpInitFuncs = (initfunc_fill_ptr_t*) malloc( " + strCountOfBlocks + " * sizeof(initfunc_fill_ptr_t) );\n")
        output.append("\t*ppInitFuncs = pInitFuncs;\n")
        for i in range(0, countOfBlocks):
            index = str(i)
            output.append("\tpInitFuncs[" + index + "] = Block" + index + "FillInitialValues;\n")
        output.append("}\n\n")
        
        output.append("void releaseInitFuncArray(initfunc_fill_ptr_t* InitFuncs){\n\tfree(InitFuncs);\n}\n\n")
        
        return ''.join(output)
    
    def __generateGetBoundFuncArray(self, totalArrWithFunctionNames, countOfBlocks, dimension):
        output = list(["void getBoundFuncArray(boundfunc_ptr_t** ppBoundFuncs){\n"])
        output.append("\tboundfunc_ptr_t* pBoundFuncs = *ppBoundFuncs;\n")
        countOfBoundaries = (dimension == 1) * 2 + (dimension == 2) * 8 + (dimension == 3) * 26
        output.append("\tpBoundFuncs = (boundfunc_ptr_t*) malloc( ( (1 + " + str(countOfBoundaries) + ") * " + str(countOfBlocks) + ") * sizeof(boundfunc_ptr_t) );\n")
        output.append("\t*ppInitFuncs = pInitFuncs;\n\n")
        for i,funcName in enumerate(totalArrWithFunctionNames):
            index = str(i)
            output.append("\tpBoundFuncs[" + index + "] = " + funcName + ";\n")
        output.append("}\n\n")
        
        output.append("void releaseBoundFuncArray(boundfunc_ptr_t* BoundFuncs){\n\tfree(BoundFuncs);\n}\n\n")
        
        return ''.join(output)

    def generateInitials(self, blocks, initials, DirichletBoundaries, equations):
#         initials --- массив [{"Name": '', "Values": []}, {"Name": '', "Values": []}]
        countOfEquations = len(equations[0].system)
        output = list(["//===================PARAMETERS==========================//\n\n"])
        output.append(self.__generateParamFunction(equations[0].params, equations[0].paramValues[0]))
        
        output.append("//===================INITIAL CONDITIONS==========================//\n\n")
        reducedInitials = initials + DirichletBoundaries
        indepVariableList = equations[0].vars
        for initialNumber,initial in enumerate(reducedInitials):
            output.append(self.__generatePointInitial(countOfEquations, initial, initialNumber, indepVariableList))
        
#         Выбрасываем лишние поля (просто приводим вид словарей для граничных условий к виду словарей для начальных условий)
#         reducedDirichletBoundaries = list([])    
#         for dirichletBoundary in DirichletBoundaries:
#             reducedDirichletBoundary = {"Name" : dirichletBoundary["Name"], "Values" : dirichletBoundary["Values"]}
        
        countOfInitials = len(reducedInitials)
        for blockNumber, block in enumerate(blocks):
            output.append(self.__generateFillFunctionForBlock(blockNumber, countOfInitials, indepVariableList))
        
        output.append(self.__generateGetInitFuncArray(len(blocks)))
        
        return ''.join(output)                     

    def generateAllFunctions(self, blocks, equations, bounds, initials, gridStep):
#         Важный момент: всегда предполагается, что массив equations содержит только 1 уравнение.
#         gridStep --- список [gridStepX, gridStepY, gridStepZ]
        userIndepVariables = equations[0].vars
        defaultIndepVariables = ['x','y','z']
        params = equations[0].params
        
        dim = len(userIndepVariables)

        cellsizeList = list([])
        allBlockSizeList = list([])
        allBlockOffsetList = list([])
        for block in blocks:
#             Количество уравнений системы --- как раз и есть cellsize
            cellsizeList.append(len(equations[block.defaultEquation].system))
            if dim == 1:
                blockSizeList = [block.sizeX,0,0]
                blockOffsetList = [block.offsetX,0,0]
            elif dim == 2:
                blockSizeList = [block.sizeX,block.sizeY,0]
                blockOffsetList = [block.offsetX,block.offsetY,0]
            else: 
                blockSizeList = [block.sizeX,block.sizeY,block.sizeZ]
                blockOffsetList = [block.offsetX,block.offsetY,block.offsetZ]
            allBlockSizeList.append(blockSizeList)
            allBlockOffsetList.append(blockOffsetList)
        
        outputStr = '#indlude <Math.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include "../hybriddomain/doc/userfuncs.h"\n\n'
        outputStr += self.generateAllDefinitions(len(params), defaultIndepVariables, gridStep, allBlockOffsetList, allBlockSizeList, cellsizeList)
        
        DirichletBoundaries = list([])
        for boundary in bounds:
            if boundary.btype == 0:
                DirichletBoundaries.append(boundary)
        outputStr += self.generateInitials(blocks, initials, DirichletBoundaries, equations)
        
        totalArrWithFunctionNames = []
        for blockNumber,block in enumerate(blocks):
            estrList = equations[block.defaultEquation].system
            cf = self.generateCentralFunctionCode(block, blockNumber, estrList, defaultIndepVariables, userIndepVariables, params)
            
#             Этот массив потом будет использован для генерирования функции-заполнителя 
            if dim == 1:
                arrWithFunctionNames = ["Block" + str(blockNumber) + "CentralFunction"]
            elif dim == 2:
                arrWithFunctionNames = ["Block" + str(blockNumber) + "CentralFunction",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex0_2",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex1_2",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex0_3",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex1_3"]
            
#             dbf = self.generateDefaultBoundaryFunction(block, blockNumber, estrList, defaultIndepVariables, userIndepVariables, params)
            bf = self.generateAllBoundaries(block, blockNumber, arrWithFunctionNames, estrList, bounds, defaultIndepVariables, userIndepVariables, params)
            totalArrWithFunctionNames += arrWithFunctionNames
            outputStr += cf + bf
            
        final = self.__generateGetBoundFuncArray(totalArrWithFunctionNames, len(blocks), len(userIndepVariables))
        outputStr += final
         
        return outputStr
    
#            Комментарий новый
# Новый комментарий