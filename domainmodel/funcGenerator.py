# -*- coding: utf-8 -*-
import numpy as np
import itertools
from equationParser import MathExpressionParser

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
    
    def __generateDerivative(self, outputList, blockNumber, parsedDrivativeExpression, varIndex, fullIndepVarList, tupleList):
# Эта функция должна правильно определить параметры для передачи их в функцию generateCodeForDerivative()
#         Если dictionary пуст, то надо сделать производную для центральной функции
#         Если длина словаря dictionary равна одному, то надо сделать условие на границу отрезка или на сторону прямоугольника или параллелепипеда
#         Если длина словаря dictionary равна двум и длина массива indepVrbls равна двум, то надо сделать условие на угол прямоугольника
#         Если длина словаря dictionary равна двум а длина массива indepVrbls равна трем, то надо сделать условие на ребро
#         Если длина словаря dictionary равна трем, то надо сделать условие на угол параллелепипеда
# Считается, что все граничные условия --- условия Неймана.
        dcg = DerivativeCodeGenerator()
        boundaryConditionCount = len(tupleList)
        
        indepVarList = list([])
        indepVarIndexList = list([])
        orderList = list([])
        for i,symbol in enumerate(parsedDrivativeExpression):
            if symbol == '{':
                indepVarList.extend([parsedDrivativeExpression[i+1]])
                indepVarIndexList.extend([fullIndepVarList.index(parsedDrivativeExpression[i+1])])
                orderList.extend([parsedDrivativeExpression[i+3]])
        
#         Условие для генерирования производных в центральных функциях
        if boundaryConditionCount == 0:    
            boundaryIndicator = -1
            parsedMathFunction = 'empty string'
            derivative = dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, fullIndepVarList, parsedMathFunction, boundaryIndicator)
#         Условие для обычной границы
        elif boundaryConditionCount == 1:
            boundaryIndicator = tupleList[0][0]
            parsedMathFunction = tupleList[0][1][varIndex]
            derivative = dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, fullIndepVarList, parsedMathFunction, boundaryIndicator)
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
                derivativeLR.extend([dcg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, fullIndepVarList, parsedMathFunction, boundaryIndicator)])   
            
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
     
    def generateBoundaryValueCode(self, parsedMathFunction, independentVariableList, independentVariableValueList):
        outputList = list([])
        operatorList = ['+','-','*','/']
          
        for j,expressionList in enumerate(parsedMathFunction):
            if expressionList[0] == '^':
                self.__generateCodeForPower(parsedMathFunction[j-1], outputList, expressionList)
            elif expressionList in operatorList:
                outputList.extend([' ' + expressionList + ' '])
            elif expressionList in independentVariableList:
                ind = independentVariableList.index(expressionList)
                outputList.extend(independentVariableValueList[ind])
            else:
                outputList.extend(expressionList)
     
        string = ''.join(outputList)
        return string
    
    def generateRightHandSideCode(self, blockNumber, leftHandSide, rightHandSide, indepVrbls, vrbls, params, tupleList = list([])):
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
                self.__generateDerivative(outputList, blockNumber, expressionList, varIndex, indepVrbls, tupleList)
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
    
    def generateCodeForDerivative(self, blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, fullIndepVarList, parsedMathFunction, boundaryIndicator):
        strideList = list([])
        for indepVar in fullIndepVarList:
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
                return self.__specialPureDerivativeAlternative(blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, fullIndepVarList, 1)
            elif (boundaryIndicator - 1) % 2 == 0 and indepVarIndexList[0] == (boundaryIndicator - 1) / 2:
                return self.__specialPureDerivativeAlternative(blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, fullIndepVarList, 0)
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
            indepVarCond1 = (indepVarList[0] == fullIndepVarList[0] and indepVarList[1] == fullIndepVarList[1]) or (indepVarList[1] == fullIndepVarList[0] and indepVarList[0] == fullIndepVarList[1])
            blockDimension = len(fullIndepVarList)
            if blockDimension > 2:
                indepVarCond2 = (indepVarList[0] == fullIndepVarList[0] and indepVarList[1] == fullIndepVarList[2]) or (indepVarList[1] == fullIndepVarList[0] and indepVarList[0] == fullIndepVarList[2])
                indepVarCond3 = (indepVarList[0] == fullIndepVarList[1] and indepVarList[1] == fullIndepVarList[2]) or (indepVarList[1] == fullIndepVarList[1] and indepVarList[0] == fullIndepVarList[2])
            
            if (bCond1 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond3):
                ind = indepVarList.index(fullIndepVarList[1])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, fullIndepVarList, 1)
            elif (blockDimension > 2 and bCond1 and indepVarCond2) or (blockDimension > 2 and bCond2 and indepVarCond3):
                ind = indepVarList.index(fullIndepVarList[2])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, fullIndepVarList, 2)
            elif (bCond2 and indepVarCond1) or (blockDimension > 2 and bCond3 and indepVarCond2):
                ind = indepVarList.index(fullIndepVarList[0])
                specialIncrement = 'D' + indepVarList[ind].upper() + 'M' + derivativeOrderList[ind]
                return self.__specialMixedDerivativeAlternative(parsedMathFunction, specialIncrement, strideList, generalOrder, fullIndepVarList, 0)
            else:
                return self.__commonMixedDerivativeAlternative(blockNumber, increment, indepVar_Order_Stride, varIndex)
        else:
            raise SyntaxError('Mixed partial derivative has very high order (greater then 2)!')
                  
class FunctionCodeGenerator:
# Генерирует выходную строку для записи в файл
    def generateAllDefinitions(self, indepVariables, DList, allBlockSizeLists, cellsizeList):
# gridStepList = [xStep, yStep, zStep]
# allBlockSizeLists = [[Block0SizeX, Block0SizeY, Block0SizeZ], [Block1SizeX, Block1SizeY, Block1SizeZ]}, ...]
# cellsizeList= [Block0CELLSIZE, Block1CELLSIZE, ...]

# allStrideLists --- это список strideОВ для каждого блока: [[block0StrideX,block0StrideY,block0StrideZ],[block1StrideX,Y,Z], ...]
# allCountLists --- аналогичный список, только для countОВ
# DList = [DX,DY,DZ]
# D2List = [DX2,DY2,DZ2]
# DM2List = [DXM2,DYM2,DZM2]
#         Требуем, чтобы длины всех массивов были одинаковы
        if len(DList) != len(indepVariables):
            raise AttributeError("A list 'gridStep' should be consist of values for ALL independent variables!")
        if len(allBlockSizeLists) != len(cellsizeList):
            raise AttributeError("Number of elements in 'allBlockSizeLists' and 'cellsizeList' should be the same!")
        
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
                    strideList.append(countList[indepVarIndex - 1])
                else:
                    strideList.append(countList[indepVarIndex - 2] * countList[indepVarIndex - 1])
            allStrideLists.append(strideList)
        
#         Создаем дефайны
        definitions = list()
        for (indepVar, d, d2, dm1, dm2) in zip(indepVariables, DList, D2List, DM1List, DM2List):
            definitions.append('#define D' + indepVar.upper() + ' ' + str(d) + '\n')
            definitions.append('#define D' + indepVar.upper() + '2 ' + str(d2) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M1 ' + str(dm1) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M2 ' + str(dm2) + '\n\n')
        for blockNumber,(strideList, countList, cellsize) in enumerate(zip(allStrideLists, allCountLists, cellsizeList)):
            definitions.append('#define Block' + str(blockNumber) + 'CELLSIZE' + ' ' + str(cellsize) + '\n\n')
            for (indepVar, stride, count) in zip(indepVariables, strideList, countList):
                definitions.append('#define Block' + str(blockNumber) + 'Stride' + indepVar.upper() + ' ' + str(stride) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Count' + indepVar.upper() + ' ' + str(count) + '\n\n')
        return ''.join(definitions)
        
    def __determineNameOfBoundary(self, boundaryNumber):
# Эта функция создана исключительно для красоты и понятности вывода. По номеру границы определяет ее уравнение.
        boundaryNames = dict({0 : 'x = 0', 1 : 'x = x_max', 2 : 'y = 0', 3 : 'y = y_max', 4 : 'z = 0', 5 : 'z = z_max'})
        if boundaryNumber in boundaryNames:
            return boundaryNames[boundaryNumber]
        else:
            raise AttributeError("Error in function __determineNameOfBoundary(): argument 'boundaryNumber' should take only integer values from 0 to 5!")
    
    def __generateFunctionSignature(self, blockNumber, name, indepVariableList, strideList):
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
    
    def generateCentralFunctionCode(self, block, blockNumber, estrList, indepVrbls, params):
#         Сейчас от блоков нужны только их номера, а в идеале --- еще и уравнения
#         function = ['#include <Math.h>\n#include <stdlib.h>\n\n']
        function = list([])
        function.extend(['\n//=========================CENTRAL FUNCTION FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
        strideList = list([])
        for indepVar in indepVrbls:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function.extend(['//Central function for '+str(len(indepVrbls))+'d model for block with number ' + str(blockNumber) + '\n'])    
        function.extend(self.__generateFunctionSignature(blockNumber, 'Block' + str(blockNumber) + 'CentralFunction', indepVrbls, strideList))
            
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        
        b = BoundaryFunctionCodeGenerator()    
        for i,equationString in enumerate(estrList):
            equationRightHandSide = parser.parseMathExpression(equationString,variables,params,indepVrbls)
            function.extend([b.generateRightHandSideCode(blockNumber,variables[i],equationRightHandSide,indepVrbls,variables,params)])
        function.extend(['}\n'])
        
        return ''.join(function) + '\n'
    
    def __generateDirichlet(self, blockNumber, name, indepVrbls, params, parsedBoundaryConditionList):
        strideList = list([])
        for indepVar in indepVrbls:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function = self.__generateFunctionSignature(blockNumber, name, indepVrbls, strideList)
        
        indepVarValueList = list([])
        for indepVar in indepVrbls:
            indepVarValueList.extend(['idx' + indepVar.upper()])
        indepVarValueList.extend(['t'])
        
        b = BoundaryFunctionCodeGenerator()
        if len(parsedBoundaryConditionList) > 1:
#             Хотя это бред, потому что я хочу использовать эту функцию для генерирования условий на углы и ребра
            raise AttributeError("Error in function __generateDirichlet(): argument 'parsedBoundaryConditionList' should contain only 1 element!")
        for i,boundary in enumerate(parsedBoundaryConditionList[0][1]):
            boundaryExpression = b.generateBoundaryValueCode(boundary, indepVrbls, indepVarValueList)
            result = '\t result[idx + ' + str(i) + '] = ' + boundaryExpression + ';\n'
            function.extend([result])
        function.extend(['}\n'])
        
        return ''.join(function)
        
    def __generateNeumann(self, blockNumber, name, parsedEstrList, variables, indepVrbls, params, parsedBoundaryConditionList): 
#         parsedBoundaryConditionList --- это список, содержащий от 1 до 3 кортежей (Номер границы, РАСПАРСЕННЫЕ граничные условия)
#         parsedEstrList --- список, элементы которого --- распарсенные правые части всех уравнений
        strideList = list([])
        for indepVar in indepVrbls:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        
        function = self.__generateFunctionSignature(blockNumber, name, indepVrbls, strideList)
            
        b = BoundaryFunctionCodeGenerator()
        for i,equation in enumerate(parsedEstrList):
            function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equation, indepVrbls, variables, params, parsedBoundaryConditionList)])
        function.extend(['}\n'])
        
        return ''.join(function)
    
    def __rectangleNearSegment(self, ribCoordinateMin, ribCoordinateMax, rectCoordinateList):
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
                pointsOnRib = self.__rectangleNearSegment(ribCoordinateMin, ribCoordinateMax, boundaryCondition[1])
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
                    
    def __generateAngleAndRibFunctions(self, blockNumber, blockRanges, parsedEstrList, variables, indepVrbls, params, parsedBoundaryConditionDictionary):
#         blockRanges --- это словарь {'min' : [x_min,y_min,z_min], 'max' : [x_max,y_max,z_max]}
#         parsedBoundaryConditionDictionary --- это словарь вида {Номер границы : [(распарсенное условие 1, [4 или 2 координаты краев части 1 границы], Тип условия),
#                                                                                  (распарсенное условие 2, [4 или 2 координаты краев части 2 границы], Тип условия), ...]}
#         В двумерном случае [координаты краев части 1 границы] содержат две точки, а в трехмерном --- четыре
        output = list([])
        
        defuaultBoundaryConditionValues = list([])
        for var in variables:
            defuaultBoundaryConditionValues.extend(['0.0'])
        
        blockDimension = len(indepVrbls)
#         Двумерный случай
        if blockDimension == 2:
            angles = [(0,2),(0,3),(1,2),(1,3)]
            anglesCoordinates = [(blockRanges['min'][0], blockRanges['min'][1]),(blockRanges['min'][0], blockRanges['max'][1]),
                                 (blockRanges['max'][0], blockRanges['min'][1]),(blockRanges['max'][0], blockRanges['max'][1])]
#             Для каждого угла ищутся граничные условия, заданные пользователем. Если находятся, то используются они,
#             а иначе используются дефолтные
            for i,angle in enumerate(angles):
#                 Делается преобразование в множество потому, что для множеств определена операция isdisjoint()
                c = set([anglesCoordinates[i]])
                
                bound1CondValue = defuaultBoundaryConditionValues
                bound2CondValue = defuaultBoundaryConditionValues
                type1 = 1
                type2 = 1
                
                if angle[0] in parsedBoundaryConditionDictionary:
                    bound1CondList = parsedBoundaryConditionDictionary[angle[0]]
                    for boundCondition in bound1CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound1CondValue = boundCondition[0]
#                             Запоминаем типы условий, чтобы потом генерировать либо Дирихле либо Неймана!
                            type1 = boundCondition[2]
                            if type1 != 0 and type1 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if angle[1] in parsedBoundaryConditionDictionary:
                    bound2CondList = parsedBoundaryConditionDictionary[angle[1]]
                    for boundCondition in bound2CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound2CondValue = boundCondition[0]
                            type2 = boundCondition[2]
                            if type2 != 0 and type2 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if bound1CondValue == defuaultBoundaryConditionValues and bound2CondValue == defuaultBoundaryConditionValues:
                    continue
                boundaryName1 = self.__determineNameOfBoundary(angle[0])
                boundaryName2 = self.__determineNameOfBoundary(angle[1])
                output.extend(['//Non-default boundary condition for ANGLE between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                if type1 == type2 == 1:
                    boundaryConditionList = list([tuple((angle[0], bound1CondValue)), tuple((angle[1], bound2CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'NeumannBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((angle[0], bound1CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'DirichletBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForAngle, indepVrbls, params, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((angle[1], bound2CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'DirichletBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForAngle, indepVrbls, params, boundaryConditionList)])

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
                        if len(self.__rectangleNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((boundaryCondition[0],boundaryCondition[2]), (defuaultBoundaryConditionValues,1)))
                elif rib[0] not in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                    for boundaryCondition in parsedBoundaryConditionDictionary[rib[1]]:
                        if len(self.__rectangleNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((defuaultBoundaryConditionValues,1), (boundaryCondition[0],boundaryCondition[2])))
                else:
                    continue
                for number,pair in enumerate(pairsOfBoundaryCondition):
                    output.extend(['//Non-default boundary condition for RIB between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + ' with number ' + str(number) + '\n'])
                    if pair[0][1] == pair[1][1] == 1:
                        nameForRib = 'Block' + str(blockNumber) + 'NeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0])), tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateNeumann(blockNumber, nameForRib, parsedEstrList, variables, indepVrbls, params, boundaryConditionList)])
                    elif pair[0][1] == 0:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, indepVrbls, params, boundaryConditionList)])
                    else:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, indepVrbls, params, boundaryConditionList)])
            
            angles = [(0,2,4),(0,2,5),(0,3,4),(0,3,5),(1,2,4),(1,2,5),(1,3,4),(1,3,5)]
            anglesCoordinates = [(blockRanges['min'][0], blockRanges['min'][1], blockRanges['min'][2]),
                                 (blockRanges['min'][0], blockRanges['min'][1], blockRanges['max'][2]),
                                 (blockRanges['min'][0], blockRanges['max'][1], blockRanges['min'][2]),
                                 (blockRanges['min'][0], blockRanges['max'][1], blockRanges['max'][2]),
                                 (blockRanges['max'][0], blockRanges['min'][1], blockRanges['min'][2]),
                                 (blockRanges['max'][0], blockRanges['min'][1], blockRanges['max'][2]),
                                 (blockRanges['max'][0], blockRanges['max'][1], blockRanges['min'][2]),
                                 (blockRanges['max'][0], blockRanges['max'][1], blockRanges['max'][2])]
            
            for i,angle in enumerate(angles):
                c = set([anglesCoordinates[i]])
                    
                bound1CondValue = defuaultBoundaryConditionValues
                bound2CondValue = defuaultBoundaryConditionValues
                bound3CondValue = defuaultBoundaryConditionValues
                type1 = 1
                type2 = 1
                type3 = 1
                    
                if angle[0] in parsedBoundaryConditionDictionary:
                    bound1CondList = parsedBoundaryConditionDictionary[angle[0]]
                    for boundCondition in bound1CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound1CondValue = boundCondition[0]
                            type1 = boundCondition[2]
                            if type1 != 0 and type1 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if angle[1] in parsedBoundaryConditionDictionary:
                    bound2CondList = parsedBoundaryConditionDictionary[angle[1]]
                    for boundCondition in bound2CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound2CondValue = boundCondition[0]
                            type2 = boundCondition[2]
                            if type2 != 0 and type2 != 1:
                                raise AttributeError("Type of boundary condition should be equal either 0 or 1!")
                            break
                if angle[2] in parsedBoundaryConditionDictionary:
                    bound3CondList = parsedBoundaryConditionDictionary[angle[2]]
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
                
                boundaryName1 = self.__determineNameOfBoundary(angle[0])
                boundaryName2 = self.__determineNameOfBoundary(angle[1])
                boundaryName3 = self.__determineNameOfBoundary(angle[2])
                output.extend(['//Non-default boundary condition for ANGLE between boundaries ' + boundaryName1 + ', ' + boundaryName2 + ' and ' + boundaryName3 + '\n'])
                if type1 == type2 == type3 == 1:
                    boundaryConditionList = list([tuple((angle[0], bound1CondValue)), tuple((angle[1], bound2CondValue)), tuple((angle[2], bound3CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'NeumannBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((angle[0], bound1CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'DirichletBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForAngle, indepVrbls, params, boundaryConditionList)])
                elif type2 == 0:
                    boundaryConditionList = list([tuple((angle[1], bound2CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'DirichletBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForAngle, indepVrbls, params, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((angle[2], bound3CondValue))])
                    nameForAngle = 'Block' + str(blockNumber) + 'DirichletBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForAngle, indepVrbls, params, boundaryConditionList)])

        return output
    
    def generateBoundaryFunctionsCode(self, blockNumber, blockRanges, boundaryConditionList, estrList, indepVrbls, params):
#         includes = '#include <Math.h>\n#include <stdlib.h>\n\n'
#         boundaryConditionList имеет структуру [{'values':[], 'type':тип, 'side':номер границы, 'ranges':[[xFrom,xTo],[y],[z]]}]
        outputFile = list(['\n//=============================NON-DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'])
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        
        parsedEstrList = list([])
        for equation in estrList:
            parsedEstrList.extend([parser.parseMathExpression(equation, variables, params, indepVrbls)])
        
        numberOfVariables = len(variables)
        for boundaryCondition in boundaryConditionList:
            if len(boundaryCondition['values']) != numberOfVariables:
                raise SyntaxError("The dimension of unknow vector-function is " + str(numberOfVariables) + ", but one of the input boundary conditions has other number of components!")
        
        boundaryNumberList = list([])
        parsedBoundaryConditionDictionary = dict({})
        boundaryCount = len(indepVrbls) * 2
#         Этот словарь будет помогать правильно нумеровать сишные функции
        countOfGeneratedFunction = dict({})
        for boundaryCondition in boundaryConditionList:
            
            boundaryNumber = boundaryCondition['side']
            if boundaryNumber in countOfGeneratedFunction:
                countOfGeneratedFunction[boundaryNumber] += 1
            else:
                countOfGeneratedFunction.update({boundaryNumber: 0})
                
            coordList = boundaryCondition['ranges']
#             Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
            boundaryCoordList = self.__createBoundaryCoordinates(coordList)
            
            if boundaryNumber >= boundaryCount:
                raise AttributeError("Error in boundary conditions entry: a value for the key 'side' shouldn't be greater than number of block boundaries!")
            indepVarsForBoundaryFunction = list(indepVrbls)
            indepVarsForBoundaryFunction.remove(indepVrbls[boundaryNumber // 2])
            indepVarsForBoundaryFunction.extend(['t'])
            
            parsedBoundaryCondition = list([])
            for boundary in boundaryCondition['values']:
                parsedBoundaryCondition.extend([parser.parseMathExpression(boundary, params, indepVarsForBoundaryFunction)])
            parsedBoundaryConditionTuple = list([tuple((boundaryNumber, parsedBoundaryCondition))])
            
            if boundaryNumber in parsedBoundaryConditionDictionary:
                parsedBoundaryConditionDictionary[boundaryNumber].append((parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type']))
            else:
                boundaryNumberList.extend([boundaryNumber])
                parsedBoundaryConditionDictionary.update({boundaryNumber : [(parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type'])]})
            
            boundaryName = self.__determineNameOfBoundary(boundaryNumber)
            dimension = len(indepVrbls)
            if dimension >= 1:
                xRangeForName = "xfrom = " + str(coordList[0][0]) + ", xto = " + str(coordList[0][1])
                rangesForName = xRangeForName
            if dimension >= 2:
                yRangeForName = "yfrom = " + str(coordList[1][0]) + ", yto = " + str(coordList[1][1])
                rangesForName = rangesForName + ', ' + yRangeForName
            if dimension == 3:
                zRangeForName = "zfrom = " + str(coordList[2][0]) + ", zto = " + str(coordList[2][1])
                rangesForName = rangesForName + ', ' + zRangeForName
            outputFile.extend(['//Non-default boundary condition for boundary ' + boundaryName + ' with ranges ' + rangesForName + '\n'])
            if boundaryNumber >= boundaryCount:
                raise SyntaxError('An attempt to impose the condition for boundary with non-existent number ' + str(boundaryNumber) + '! Maximal number of boundaies is equal ' + str(boundaryCount) + '!')
            if boundaryCondition['type'] == 0:
                outputFile.extend([self.__generateDirichlet(blockNumber, 'Block' + str(blockNumber) + 'DirichletBound' + str(boundaryNumber) + '_' + str(countOfGeneratedFunction[boundaryNumber]), indepVrbls, params, parsedBoundaryConditionTuple)])
            else:
                outputFile.extend([self.__generateNeumann(blockNumber, 'Block' + str(blockNumber) + 'NeumannBound' + str(boundaryNumber) + '_' + str(countOfGeneratedFunction[boundaryNumber]), parsedEstrList, variables, indepVrbls, params, parsedBoundaryConditionTuple)])
        
        outputFile.extend(self.__generateAngleAndRibFunctions(blockNumber, blockRanges, parsedEstrList, variables, indepVrbls, params, parsedBoundaryConditionDictionary))
        return ''.join(outputFile)
    
    def generateDefaultBoundaryFunction(self, block, blockNumber, estrList, indepVrbls, params):
        defaultFunctions = list([])
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
            
        parsedEstrList = list([])
        for equation in estrList:
            parsedEstrList.extend([parser.parseMathExpression(equation, variables, params, indepVrbls)])
            
        defuaultBoundaryConditionValues = list([])
        for var in variables:
            defuaultBoundaryConditionValues.extend(['0.0'])
                
        defaultFunctions.extend(['\n//=========================DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
                
        boundaryCount = len(indepVrbls) * 2
        for i in range(0,boundaryCount):
            boundaryName = self.__determineNameOfBoundary(i)
            defaultFunctions.extend(['//Default boundary condition for boundary ' + boundaryName + '\n'])
            nameForSide = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(i)
            defaultBoundaryConditionList = list([tuple((i, defuaultBoundaryConditionValues))])
            defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForSide, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
            
        if len(indepVrbls) == 2:
            angles = [(0,2),(0,3),(1,2),(1,3)]
            for angle in angles:
                boundaryName1 = self.__determineNameOfBoundary(angle[0])
                boundaryName2 = self.__determineNameOfBoundary(angle[1])
                defaultFunctions.extend(['//Default boundary condition for angle between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                defaultBoundaryConditionList = list([tuple((angle[0], defuaultBoundaryConditionValues)), tuple((angle[1], defuaultBoundaryConditionValues))])
                nameForAngle = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForAngle' + str(angle[0]) + '_' + str(angle[1])
                defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
                    
#             defaultFunctions.extend([self.__generateAngleOrRib(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
        elif len(indepVrbls) == 3:
            ribs = [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)]
            for rib in ribs:
                boundaryName1 = self.__determineNameOfBoundary(rib[0])
                boundaryName2 = self.__determineNameOfBoundary(rib[1])
                defaultFunctions.extend(['//Default boundary condition for rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                defaultBoundaryConditionList = list([tuple((rib[0], defuaultBoundaryConditionValues)), tuple((rib[1], defuaultBoundaryConditionValues))])
                nameForAngle = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1])
                defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
            angles = [(0,2,4),(0,2,5),(0,3,4),(0,3,5),(1,2,4),(1,2,5),(1,3,4),(1,3,5)]
            for angle in angles:
                boundaryName1 = self.__determineNameOfBoundary(angle[0])
                boundaryName2 = self.__determineNameOfBoundary(angle[1])
                boundaryName3 = self.__determineNameOfBoundary(angle[2])
                defaultFunctions.extend(['//Default boundary condition for angle between boundaries ' + boundaryName1 + ', ' + boundaryName2 + ' and ' + boundaryName3 + '\n'])
                defaultBoundaryConditionList = list([tuple((angle[0], defuaultBoundaryConditionValues)), tuple((angle[1], defuaultBoundaryConditionValues)), tuple((angle[2], defuaultBoundaryConditionValues))])
                nameForAngle = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForAngle' + str(angle[0]) + '_' + str(angle[1]) + '_' + str(angle[2])
                defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForAngle, parsedEstrList, variables, indepVrbls, params, defaultBoundaryConditionList)])
        
        return ''.join(defaultFunctions)
    
    def generateAllBoundaries(self, block, blockNumber, estrList, bounds, indepVrbls, params):
# Эта функция должна для блока block сгенерировать все нужные функции.
# Массив bounds имеет ту же структуру и смысл, что и в классе Model
        boundaryFunctions = list()
        blockDimension = block['Dimension']
        minRanges = [block['Offset']['x']]
        maxRanges = [block['Size']['x']]
        if blockDimension >= 2:
            minRanges = minRanges + [block['Offset']['y']]
            maxRanges = maxRanges + [block['Size']['y']]
        if blockDimension == 3:
            minRanges = minRanges + [block['Offset']['z']]
            maxRanges = maxRanges + [block['Size']['z']]
        blockRanges = dict({'min' : minRanges, 'max' : maxRanges})
#        Надо сформировать структуру boundaryConditionList = [{'values':[], 'type':тип, 'side':номер границы, 'ranges':[[xFrom,xTo],[y],[z]]}]
        boundaryConditionList = list()
        boundRegions = block['BoundRegions']
        for region in boundRegions:
            boundNumber = region['BoundNumber']
            if boundNumber >= len(bounds):
                raise AttributeError("Non-existent number of boundary condition is set for some of boundary regions in array 'Blocks'!")
            side = region['Side']
            boundaryRanges = [[region['xfrom'],region['xto']]]
            if blockDimension >= 2:
                boundaryRanges = boundaryRanges + [[region['yfrom'],region['yto']]]
            if blockDimension == 3:
                boundaryRanges = boundaryRanges + [[region['zfrom'],region['zto']]]
                
            bound = bounds[boundNumber]
            boundaryType = bound['Type']
            values = bound['Values']
                
            boundaryCondition = dict({'values': values, 'type': boundaryType, 'side': side, 'ranges': boundaryRanges})
            boundaryConditionList.append(boundaryCondition)
#         Теперь надо вызвать функцию, генерирующую граничные условия для данного блока
        boundaryFunctions.append(self.generateBoundaryFunctionsCode(blockNumber, blockRanges, boundaryConditionList, estrList, indepVrbls, params))
        return ''.join(boundaryFunctions)
    
    def generateAllFunctions(self, blocks, equations, bounds, gridStep):
        indepVrbls = equations[0]['Vars']
        params = equations[0]['Params']
        
        dim = len(indepVrbls)
        DList = list([])
        DList.append(gridStep['x'])
        if dim >= 2:
            DList.append(gridStep['y'])
        if dim == 3:
            DList.append(gridStep['z'])
        
        cellsizeList = list([])
        allBlockSizeList = list([])
        for block in blocks:
#             Количество уравнений системы --- как раз и есть cellsize
            cellsizeList.append(len(equations[block['DefaultEquation']]['System']))
            blockSizeList = [block['Size']['x']]
            if dim >= 2:
                blockSizeList.append(block['Size']['y'])
            if dim == 3:
                blockSizeList.append(block['Size']['z'])
            allBlockSizeList.append(blockSizeList)
        
        outputStr = "#indlude <Math.h>\n#include <stdio.h>\n#include <stdlib.h>\n\n"
        outputStr = outputStr + self.generateAllDefinitions(indepVrbls, DList, allBlockSizeList, cellsizeList)
        for blockNumber,block in enumerate(blocks):
            estrList = equations[block['DefaultEquation']]['System']
            cf = self.generateCentralFunctionCode(block, blockNumber, estrList, indepVrbls, params)
            dbf = self.generateDefaultBoundaryFunction(block, blockNumber, estrList, indepVrbls, params)
            bf = self.generateAllBoundaries(block, blockNumber, estrList, bounds, indepVrbls, params)
            outputStr = outputStr + cf + dbf + bf
         
        return outputStr
    
        