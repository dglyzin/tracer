# -*- coding: utf-8 -*-
from someFuncs import NewtonBinomCoefficient, generateCodeForMathFunction

class DerivGenerator:
#     Этот класс должен в функции generateRightHandSideCode() создавать производную, когда это будет надо.
    # Этот класс отвечает за генерирование кода для производных                       
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
                indicesListAsString.extend([' + ' + str(int(index))])
            else:
                indicesListAsString.extend([str(int(index))])
        return indicesListAsString
    
    def __createCoefficientList(self, derivativeOrder):
# Т.к. для CentralFunction умеем генерировать аппроксимации производных любого порядка, то эти аппроксимации содержат много
# слагаемых, перед каждым из которых имеется свой коэффициент
        numberList = [NewtonBinomCoefficient(derivativeOrder, k) for k in range(0, derivativeOrder + 1)]
        stringList = []
        for number in numberList:
            stringList.extend([str(number)])
        return stringList
    
    def __commonMixedDerivativeAlternative(self, blockNumber, increment, indepVar_Order_Stride_List, varIndex):
# Способ генерирования кода для смешанной производной для CentralFunction и иногда для граничных функций
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
            
            right = generateCodeForMathFunction(parsedMathFunction, fullIndepVarList, fullIndepVarValueListR)
            left = generateCodeForMathFunction(parsedMathFunction, fullIndepVarList, fullIndepVarValueListL)
            if right == left:
                return '0.0'
            else:
                return '(0.5 * ' + increment + ' * ' + '(' + right + ' - ' + left + ')' + ')'
        else:
            raise SyntaxError("The highest derivative order of the system greater than 2! I don't know how to generate boundary function in this case!")
        
#     def __singularMixedDerivativeAlternative1(self, blockNumber, increment, indicesList, varIndex, totalDerivOrder):
# #         Вариант генерирования аппроксимации частной производной для угловой клетки в случае соединения блоков    
#         if totalDerivOrder == 2:
#             first = 'source[idx' + indicesList[0] + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
#             second = ' - source[idx' + indicesList[1] + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
#             third = ' - source[idx' + indicesList[2] + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
#             fourth = ' + source[idx' + indicesList[3] + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
#             finiteDifference = first + second + third + fourth
#             return '(' + increment + ' * ' + '(' + finiteDifference + ')' + ')'
#         else:
#             raise SyntaxError("Order of some mixed partial derivative greater than 2. I don't know how to work with it!")
        
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

        boundaryValue = generateCodeForMathFunction(parsedMathFunction, fullIndepVarList, fullIndepVarValueList)
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
    
    def __interconnectPureDerivAlternative(self, blockNumber, increment, stride, order, varIndex, side, firstIndex, secondIndexSTR):
        if side % 2 == 0:
            first = 'source[idx + ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
            second = 'ic['+str(firstIndex)+'][' + secondIndexSTR + ' + ' + str(varIndex) + ']'
        else:
            first = 'ic['+str(firstIndex)+'][' + secondIndexSTR + ' + ' + str(varIndex) + ']'
            second = 'source[idx - ' + stride + ' * ' + 'Block' + str(blockNumber) + 'CELLSIZE + ' + str(varIndex) + ']'
        if order == 1:
            return '0.5 * ' + increment + ' * ' + '(' + first + ' - ' + second + ')'
        elif order == 2:
            third = '2.0 * source[idx + ' + str(varIndex) + ']'
            return '(' + increment + ' * ' + '(' + first + ' - ' + third + ' + ' + second + ')' + ')'
        else:
            raise AttributeError("Pure derivative in some equation has order greater than 2!")
        
#     def __creatreIndicesList(self, angle, blockNumber, derivativeIndepVarList, userIndepVarList):
# #         Создает список индексов для генерирования смешанной производной 2 порядка
# #         angle --- это номер угла блока: здесь y=0 --- вверху
# #         1---2
# #         |   |
# #         3---4
# #         Расстановка независимых переменных в derivativeIndepVarList в лексикографическом порядке (т.е. x всегда левее y, y - левее z и т.д.)
#         if userIndepVarList.index(derivativeIndepVarList[0]) > userIndepVarList.index(derivativeIndepVarList[1]):
#             derivativeIndepVarList.reverse()
#         indicesList = []
#         if angle == 1:
#             indicesList.append(' + (Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper() + ' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper() + ')')
#             indicesList.append(' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper())
#             indicesList.append(' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper())
#             indicesList.append('0')
#         elif angle == 2:
#             indicesList.append(' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper())
#             indicesList.append(' - (Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper() + ' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper() + ')')
#             indicesList.append('0')
#             indicesList.append(' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper())
#         elif angle == 3:
#             indicesList.append(' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper())
#             indicesList.append('0')
#             indicesList.append(' + (Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper() + ' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper() + ')')
#             indicesList.append(' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper())
#         elif angle == 4:
#             indicesList.append('0')
#             indicesList.append(' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper())
#             indicesList.append(' - Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper())
#             indicesList.append(' - (Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[0].upper() + ' + Block' + str(blockNumber) + 'Stride' + derivativeIndepVarList[1].upper() + ')')
    
    def generateCodeForDerivative(self, blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex = -1, secondIndexSTR = '0'):
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
            
            #Случай соединения блоков в одномерной задаче
            if firstIndex >= 0:
                if side / 2 == indepVarIndexList[0]:
                    return self.__interconnectPureDerivAlternative(blockNumber, increment, stride, order, varIndex, side, firstIndex, secondIndexSTR)
                else:
                    return self.__commonPureDerivativeAlternative(blockNumber, increment, stride, order, varIndex)
            else:
                if side % 2 == 0 and indepVarIndexList[0] == side / 2:
                    return self.__specialPureDerivativeAlternative(blockNumber, parsedMathFunction, increment, specialIncrement, stride, strideList, order, varIndex, userIndepVariables, 1)
                elif (side - 1) % 2 == 0 and indepVarIndexList[0] == (side - 1) / 2:
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
                
            bCond1 = side == 0 or side == 1
            bCond2 = side == 2 or side == 3
            bCond3 = side == 4 or side == 5
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
        