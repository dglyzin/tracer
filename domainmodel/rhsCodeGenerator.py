# -*- coding: utf-8 -*-
import numpy as np
from derivCodeGenerator import DerivGenerator

class RHSCodeGenerator:
# Генерирует код правой части уравнения в случае центральной функции, Неймановского кр. усл-я, соединения.    
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
    
    def __generateDerivative(self, outputList, blockNumber, parsedDrivativeExpression, varIndex, userIndepVariables, pbcl):
# Эта функция должна правильно определить параметры для передачи их в функцию generateCodeForDerivative()
#         Если pbcl пуст, то надо сделать производную для центральной функции
#         Если длина словаря pbcl равна одному, то надо сделать условие на границу отрезка или на сторону прямоугольника или параллелепипеда
#         Если длина словаря pbcl равна двум и длина массива indepVrbls равна двум, то надо сделать условие на угол прямоугольника
#         Если длина словаря pbcl равна двум а длина массива indepVrbls равна трем, то надо сделать условие на ребро
#         Если длина словаря pbcl равна трем, то надо сделать условие на угол параллелепипеда
        dg = DerivGenerator()
        boundaryConditionCount = len(pbcl)
        
        indepVarList = list()
        indepVarIndexList = list()
        orderList = list()
        for i,symbol in enumerate(parsedDrivativeExpression):
            if symbol == '{':
                indepVarList.append(parsedDrivativeExpression[i+1])
                indepVarIndexList.append(userIndepVariables.index(parsedDrivativeExpression[i+1]))
                orderList.append(parsedDrivativeExpression[i+3])
        
#         Условие для генерирования производных в центральных функциях
        if boundaryConditionCount == 0:    
            side = -1
            parsedMathFunction = 'empty string'
            derivative = dg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)
#         Условие для обычной границы ИЛИ ДЛЯ СОЕДИНЕНИЯ!!!
        elif boundaryConditionCount == 1:
            side = pbcl[0].side
            if pbcl[0].name == "BoundCondition":
                parsedMathFunction = pbcl[0].parsedValues[varIndex]
                derivative = dg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)
            else:
                derivative = dg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, "", side, pbcl[0].index)
#         Условие на угол прямоугольника или параллелепипеда или на ребро параллелепипеда        
        elif boundaryConditionCount == 2 or boundaryConditionCount == 3:
            derivativeLR = list([])
            for index in indepVarIndexList:
                if index == pbcl[0].side // 2:
                    parsedMathFunction = pbcl[0].parsedValues[varIndex]
                    side = pbcl[0].side                        
                elif index == pbcl[1].side // 2:
                    parsedMathFunction = pbcl[1].parsedValues[varIndex]
                    side = pbcl[1].side
                elif boundaryConditionCount == 3 and index == pbcl[2].side // 2:
                    parsedMathFunction = pbcl[2].parsedValues[varIndex]
                    side = pbcl[2].side
                else:
                    side = -1
                    parsedMathFunction = 'empty string'
                derivativeLR.extend([dg.generateCodeForDerivative(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)])   
            
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

    def generateRightHandSideCode(self, blockNumber, leftHandSide, rightHandSide, userIndepVariables, vrbls, params, pbcl = []):
#         pbcl (parsedBoundaryConditionList) --- это список, содержащий от 1 до 3 граничных условий
#         rightHandSide -- распарсенная правая часть уравнения, массив строк.
        varIndex = vrbls.index(leftHandSide)
        result = '\t result[idx + ' + str(varIndex) + '] = '
        outputList = list([result])
        elemFuncsList = ['exp','sin','sinh','cos','tan','tanh','sqrt','log']
        operatorList = ['+','-','*','/']
        
        for j,expressionList in enumerate(rightHandSide):
            if expressionList[0] == 'D[':
                varIndex = vrbls.index(expressionList[1])
                self.__generateDerivative(outputList, blockNumber, expressionList, varIndex, userIndepVariables, pbcl)
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