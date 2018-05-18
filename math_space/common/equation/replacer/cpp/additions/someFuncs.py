# -*- coding: utf-8 -*-

def getCellCountInHalfInterval(lengthInCoords, step):
    count = lengthInCoords/step
    return int(round(count))

def getCellIndex(lengthInCoords, step):
    #lengthInCoords= coordinate of the cell we need
    #returns index of the cell
    count = lengthInCoords/step
    return int(round(count))

def getCellCountInClosedInterval(lengthInCoords, step):
    count = lengthInCoords/step
    return int(round(count)) + 1

def getRangesInHalfInterval(XData, YData = [], ZData = []):
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
            firstCellIdxVar = getCellIndex(varFrom, stepVar)
            lastCellIdxVar = getCellIndex(varTo, stepVar)
            ranges += [firstCellIdxVar, lastCellIdxVar]
        return ranges
    
def getRangesInClosedInterval(XData, YData = [], ZData = []):
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
            firstCellIdxVar = getCellIndex(varFrom, stepVar)
            lastCellIdxVar = getCellIndex(varTo, stepVar) + 1            
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
    '''
    DESCRIPTION:
    Генерирует сишный код для какой-то математической функции.
    
    INPUT:
    userIndepVariables - те переменные, которые ввел юзер,
    independentVariableValueList - те выражения, которые должны быть подставлены вместо них;
    parsedMathFunction - распарсенная с помощью equationParser математическая функция
    '''
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

def squareOrVolume(xlist, ylist, zlist = []):
        l1 = abs(xlist[0] - xlist[1])
        l2 = abs(ylist[0] - ylist[1])
        if len(zlist) == 2:
            l3 = abs(zlist[0] - zlist[1])
        else:
            l3 = 1
        return l3 * l2 * l1
    
def splitBigRect(bigRect, smallRect):
    #Функция разбивает результат вычитания внутреннего (маленького) прямоугольника из внешнего (большого)
    #на минимальное количество прямоугольников;
    #!!!Работа происходит с координатами относительно блока!!!
    #bigRect = [xfrom, xto, yfrom, yto] и аналогично smallRect; возвращается массив прямоугольников в таком же формате
    
    #Внутренний пр-к совпадает с внешним
    if bigRect[0] == smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] == smallRect[3]:
        return []
    #Прямоугольники отличаются только одной из сторон
    elif bigRect[0] != smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] == smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] == smallRect[3]:
        return [[smallRect[1], bigRect[1], bigRect[2], bigRect[3]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] == smallRect[3]:
        return [[bigRect[0], bigRect[1], bigRect[2], smallRect[2]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], bigRect[1], smallRect[3], bigRect[3]]]
    #Прямоугольники отличаются двумя сторонами
    #Внутренний пр-к - Вертикальная полоса
    elif bigRect[0] != smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] == smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[1], bigRect[1], bigRect[2], bigRect[3]]]
    #Внутренний пр-к - Горизонтальная полоса
    elif bigRect[0] == smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], bigRect[1], bigRect[2], smallRect[2]], [bigRect[0], bigRect[1], smallRect[3], bigRect[3]]]
    #Прямоугольники имеют общий угол
    elif bigRect[0] != smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] == smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], bigRect[2], smallRect[2]]]
    elif bigRect[0] != smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], smallRect[3], bigRect[3]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] == smallRect[3]:
        return [[smallRect[1], bigRect[1], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], bigRect[2], smallRect[2]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] != smallRect[3]:
        return [[smallRect[1], bigRect[1], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], smallRect[3], bigRect[3]]]
    #Прямоугольники имеют только одну общую сторону
    elif bigRect[0] != smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] == smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[1], bigRect[1], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], bigRect[2], smallRect[2]]]
    elif bigRect[0] != smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] == smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[1], bigRect[1], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], smallRect[3], bigRect[3]]]
    elif bigRect[0] == smallRect[0] and bigRect[1] != smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], bigRect[1], bigRect[2], smallRect[2]], [bigRect[0], bigRect[1], smallRect[3], bigRect[3]], [smallRect[1], bigRect[1], smallRect[2], smallRect[3]]]
    elif bigRect[0] != smallRect[0] and bigRect[1] == smallRect[1] and bigRect[2] != smallRect[2] and bigRect[3] != smallRect[3]:
        return [[bigRect[0], bigRect[1], bigRect[2], smallRect[2]], [bigRect[0], bigRect[1], smallRect[3], bigRect[3]], [bigRect[0], smallRect[0], smallRect[2], smallRect[3]]]
    #Прямоугольники не имеют общих сторон
    else:
        return [[bigRect[0], smallRect[0], bigRect[2], bigRect[3]], [smallRect[1], bigRect[1], bigRect[2], bigRect[3]], [smallRect[0], smallRect[1], bigRect[2], smallRect[2]], [smallRect[0], smallRect[1], smallRect[3], bigRect[3]]]
    
def intersectionOfRects(rect1, rect2):
    #Если прямоугольники пересекаются, то возвращает координаты вхождения rect2 в rect1, иначе - пустой список
    #rect1 = [xfrom, xto, yfrom, yto] и rect2 аналогичен
    intersection = [max([rect1[0], rect2[0]]), min([rect1[1], rect2[1]]), max([rect1[2], rect2[2]]), min([rect1[3], rect2[3]])]
    #Если xfrom >= xto или yfrom >= yto, то пересечения нет! В этом случае возвращается пустой список
    if intersection[0] >= intersection[1] or intersection[2] >= intersection[3]:
        return []
    else:
        return intersection
    
def determineCellIndexOfStartOfConnection2D(icRegion):
    #Если эта разность нулевая, то сединение находится в начале стороны блока, поэтому индекс = 0.
    if icRegion.lenBetweenStartOfBlockSideAndStartOfConnection == 0:
        return 0
    else:
    #Найдем количество клеток между ними. Оно и будет индексом клетки, стоящей в начале соединения
        return getCellIndex(icRegion.lenBetweenStartOfBlockSideAndStartOfConnection, icRegion.stepAlongSide)
