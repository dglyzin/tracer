# -*- coding: utf-8 -*-
import numpy as np
from derivCodeGenerator import PureDerivGenerator, MixDerivGenerator

class RHSCodeGenerator:
# Генерирует код правой части уравнения в случае центральной функции, Неймановского кр. усл-я, соединения.    
    def generateCodeForPower(self, preventElementInParsedExpression, creatingOutputList, expressionWithPower):
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
                self.callDerivGenerator(outputList, blockNumber, expressionList, varIndex, userIndepVariables, pbcl)
            elif expressionList in vrbls:
                # если переменная не в конце и за ней стоит скобка -- запаздывание
                if j != len(rightHandSide)-1 and rightHandSide[j+1] == '(':
                    outputList.extend(['DELAY'])
                else:
                    varIndex = vrbls.index(expressionList)
                    outputList.extend(['source[idx + ' + str(varIndex) + ']'])
            elif expressionList in params:
                parIndex = params.index(expressionList)
                outputList.extend(['params[' + str(parIndex) + ']'])
            elif expressionList in operatorList:
                outputList.extend([' ' + expressionList + ' '])
            elif expressionList[0] == '^':
                self.generateCodeForPower(rightHandSide[j-1], outputList, expressionList)
            elif expressionList in elemFuncsList:
                outputList.extend([expressionList])
            else:
                outputList.extend([expressionList])
    
        string = ''.join(outputList) + ';\n'
        return string
    
    def callDerivGenerator(self, outputList, blockNumber, parsedDrivativeExpression, varIndex, userIndepVariables, pbcl):
        # Эта функция должна правильно определить параметры для передачи их в функцию callSpecialDerivGenerator()
        #     Если pbcl пуст, то надо сделать производную для центральной функции
        #     Если длина словаря pbcl равна одному, то надо сделать условие на границу отрезка или на сторону прямоугольника или параллелепипеда
        #     Если длина словаря pbcl равна двум и длина массива indepVrbls равна двум, то надо сделать условие на угол прямоугольника
        #     Если длина словаря pbcl равна двум а длина массива indepVrbls равна трем, то надо сделать условие на ребро
        #     Если длина словаря pbcl равна трем, то надо сделать условие на угол параллелепипеда
        boundaryConditionCount = len(pbcl)
        
        indepVarList = list()
        indepVarIndexList = list()
        orderList = list()
        for i,symbol in enumerate(parsedDrivativeExpression):
            if symbol == '{':
                indepVarList.append(parsedDrivativeExpression[i+1])
                indepVarIndexList.append(userIndepVariables.index(parsedDrivativeExpression[i+1]))
                orderList.append(parsedDrivativeExpression[i+3])
        
        #Условие для генерирования производных в центральных функциях
        if boundaryConditionCount == 0:    
            side = -1
            parsedMathFunction = 'empty string'
            derivative = self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)
        #Условие для обычной границы ИЛИ ДЛЯ СОЕДИНЕНИЯ!!!
        elif boundaryConditionCount == 1:
            side = pbcl[0].side
            if pbcl[0].name == "BoundCondition":
                parsedMathFunction = pbcl[0].parsedValues[varIndex]
                derivative = self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)
            else:
                derivative = self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, "", side, pbcl[0].firstIndex, pbcl[0].secondIndex)
        #Условие на угол прямоугольника или параллелепипеда или на ребро параллелепипеда        
        elif boundaryConditionCount == 2 or boundaryConditionCount == 3:
            derivativeLR = list([])
            for index in indepVarIndexList:
                if index == pbcl[0].side // 2:
                    side = pbcl[0].side 
                    if pbcl[0].name == "BoundCondition":
                        parsedMathFunction = pbcl[0].parsedValues[varIndex]
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)])                     
                    else:
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, "", side, pbcl[0].firstIndex, pbcl[0].secondIndex)])
                elif index == pbcl[1].side // 2:
                    side = pbcl[1].side
                    if pbcl[1].name == "BoundCondition":
                        parsedMathFunction = pbcl[1].parsedValues[varIndex]
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)])
                    else:
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, "", side, pbcl[1].firstIndex, pbcl[1].secondIndex)])
                elif boundaryConditionCount == 3 and index == pbcl[2].side // 2:
                    side = pbcl[2].side
                    if pbcl[2].name == "BoundCondition":
                        parsedMathFunction = pbcl[2].parsedValues[varIndex]
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)])
                    else:
                        derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, "", side, pbcl[2].firstIndex, pbcl[2].secondIndex)])
                else:
                    side = -1
                    parsedMathFunction = 'empty string'
                    derivativeLR.extend([self.callSpecialDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, orderList, userIndepVariables, parsedMathFunction, side)])   
            
            if len(derivativeLR) == 1:
                derivative = derivativeLR[0]
            #Можно написать else, потому что считаем, что производные могут браться максимум второго порядка
            else:
                if derivativeLR[0] != '0.0' and derivativeLR[1] != '0.0':
                    derivative = '(0.5 * ' + derivativeLR[0] + ' + 0.5 * ' + derivativeLR[1] + ')'
                elif derivativeLR[0] == '0.0' and derivativeLR[1] != '0.0':
                    derivative = '(0.5 * ' + derivativeLR[1] + ')'
                elif derivativeLR[0] != '0.0' and derivativeLR[1] == '0.0':
                    derivative = '(0.5 * ' + derivativeLR[0] + ')'
                else:
                    derivative = '0.0'
        #Отмечаем случай, когда в знаменателе получился нуль при аппроксимации производной.
        if derivative == '0.0' and outputList[-1] == ' / ':
            raise SyntaxError("An approximation for mixed derivative" + ''.join(parsedDrivativeExpression) + ", that stands in the denominator, was identically equal to zero during the process of generating function for boundary condition!")
        outputList.extend([derivative])
        
    def callSpecialDerivGenerator(self, blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex = -1, secondIndexSTR = '0'):
        if len(indepVarList) == 1 or indepVarList[0] == indepVarList[1]: 
            pdg = PureDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex, secondIndexSTR)
            return pdg.pureDerivative()
        elif len(indepVarList) == 2:
            mdg = MixDerivGenerator(blockNumber, varIndex, indepVarList, indepVarIndexList, derivativeOrderList, userIndepVariables, parsedMathFunction, side, firstIndex, secondIndexSTR)
            return mdg.mixDerivative()
        else:
            raise SyntaxError('Mixed partial derivative has very high order (greater then 2)!')