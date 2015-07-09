# -*- coding: utf-8 -*-

import itertools

def getCellCountAlongLine(lengthInCoords, step):
    count = lengthInCoords/step#+1
    return int(count)

def getRanges(XData, YData = [], ZData = []):
        #Диапазоны в кординатах преобразует в диапазоны в клетках
        #XData = [xfrom, xto, stepX, xmax]
        allData = [XData]
        if len(YData) != 0:
            allData.append(YData)
        if len(ZData) != 0:
            allData.append(ZData)
        ranges = []
        for data in allData: 
            varFrom = data[0]
            varTo = data[1]
            stepVar = data[2]
            varMax = data[3]
            maxIdxVar = getCellCountAlongLine(varMax, stepVar)
            firstCellIdxVar = getCellCountAlongLine(varFrom, stepVar)
            lastCellIdxVar = getCellCountAlongLine(varTo, stepVar)
            if firstCellIdxVar == lastCellIdxVar == maxIdxVar:
                firstCellIdxVar -= 1
            elif firstCellIdxVar == lastCellIdxVar:
                lastCellIdxVar += 1
            ranges += [firstCellIdxVar, lastCellIdxVar]
        return ranges

def factorial(number):
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
    
def NewtonBinomCoefficient(n, k):
# Вычисляет биномиальные коэффициенты затем, чтобы потом их использовать как коэффициенты для конечных разностей
    if n < k:
        raise AttributeError("n souldn't be less then k!")
    return factorial(n) / (factorial(k) * factorial(n-k))
    
def generateCodeForMathFunction(parsedMathFunction, userIndepVariables, independentVariableValueList):
# Генерирует сишный код для какой-то математической функции. userIndepVariables - те переменные, которые ввел юзер,
# independentVariableValueList - те выражения, которые должны быть подставлены вместо них;
# parsedMathFunction - распарсенная с помощью equationParser математическая функция
    outputList = list([])
    operatorList = ['+','-','*','/']
    
    from rhsCodeGenerator import RHSCodeGenerator
    powerGenerator = RHSCodeGenerator()      
    for j,expressionList in enumerate(parsedMathFunction):
        if expressionList[0] == '^':
            powerGenerator.generateCodeForPower(parsedMathFunction[j-1], outputList, expressionList)
        elif expressionList in operatorList:
            outputList.append(' ' + expressionList + ' ')
        elif expressionList in userIndepVariables:
            ind = userIndepVariables.index(expressionList)
            outputList.append(independentVariableValueList[ind])
        else:
            outputList.append(expressionList)
     
    return ''.join(outputList)

def determineNameOfBoundary(side):
# Эта функция создана исключительно для красоты и понятности файла Functions.cpp. По номеру границы определяет ее уравнение.
        boundaryNames = dict({0 : 'x = 0', 1 : 'x = x_max', 2 : 'y = 0', 3 : 'y = y_max', 4 : 'z = 0', 5 : 'z = z_max'})
        if side in boundaryNames:
            return boundaryNames[side]
        else:
            raise AttributeError("Error in function __determineNameOfBoundary(): argument 'boundaryNumber' should take only integer values from 0 to 5!")
        
def convertRangesToBoundaryCoordinates(xyzList):
#         xyzList --- список вида [[xFrom, xTo], [yFrom, yTo], [zFrom, zTo]]
#         Функция по списку xyzList формирует в двумерном случае 2 точки границы [(x1,y1), (x2,y2)],
#         в 3 мерном случае -- 4 точки прямоугольника [(x1,y1), (x2,y2), (x3,y3), (x4,y4)].
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
            raise AttributeError("Dimension of geometric space should not be greater than 3!")

def RectSquare(xlist, ylist):
        l1 = abs(xlist[0] - xlist[1])
        l2 = abs(ylist[0] - ylist[1])
        return l2 * l1
    
def determineCellIndexOfStartOfConnection2D(icRegion):
    #Если эта разность нулевая, то сединение находится в начале стороны блока, поэтому индекс = 0.
    if icRegion.lenBetweenStartOfBlockSideAndStartOfConnection == 0:
        startCellIndex = 0
    else:
    #Найдем количество клеток между ними. Оно и будет индексом клетки, стоящей в начале соединения
        startCellIndex = getCellCountAlongLine(icRegion.lenBetweenStartOfBlockSideAndStartOfConnection, icRegion.stepAlongSide)
    #Определяется индекс клетки конца соединения: это индекс клетки начала + количество клеток в соединении - 1
    endCellIndex = startCellIndex + getCellCountAlongLine(icRegion.lenOfConnection, icRegion.stepAlongSide) - 1
    return startCellIndex, endCellIndex
