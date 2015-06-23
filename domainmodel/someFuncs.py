# -*- coding: utf-8 -*-

def getCellCountAlongLine(lengthInCoords, step):
    count = lengthInCoords/step#+1
    return int(count)

def factorial(self, number):
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
    
def NewtonBinomCoefficient(self, n, k):
# Вычисляет биномиальные коэффициенты затем, чтобы потом их использовать как коэффициенты для конечных разностей
    if n < k:
        raise AttributeError("n souldn't be less then k!")
    return factorial(n) / (factorial(k) * factorial(n-k))
    
def generateCodeForMathFunction(self, parsedMathFunction, userIndepVariables, independentVariableValueList):
# Генерирует сишный код для какой-то математической функции. userIndepVariables - те переменные, которые ввел юзер,
# independentVariableValueList - те выражения, которые должны быть подставлены вместо них;
# parsedMathFunction - распарсенная с помощью equationParser математическая функция
    outputList = list([])
    operatorList = ['+','-','*','/']
          
    for j,expressionList in enumerate(parsedMathFunction):
        if expressionList[0] == '^':
            self.__generateCodeForPower(parsedMathFunction[j-1], outputList, expressionList)
        elif expressionList in operatorList:
            outputList.append(' ' + expressionList + ' ')
        elif expressionList in userIndepVariables:
            ind = userIndepVariables.index(expressionList)
            outputList.append(independentVariableValueList[ind])
        else:
            outputList.append(expressionList)
     
    return ''.join(outputList)