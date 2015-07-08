# -*- coding: utf-8 -*-
from equationParser import MathExpressionParser
from someFuncs import generateCodeForMathFunction, determineNameOfBoundary, RectSquare, determineCellIndexOfStartOfConnection2D
from rhsCodeGenerator import RHSCodeGenerator

class FuncGenerator:
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        dimension = len(equations[0].vars)
        if dimension == 1:
            self.generator = generator1D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        elif dimension == 2:
            self.generator = generator2D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        else:
            self.generator = generator3D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
    
    def generateAllFunctions(self):
#         Важный момент: всегда предполагается, что массив equations содержит только 1 уравнение.
#         gridStep --- список [gridStepX, gridStepY, gridStepZ]
        outputStr = '#include <math.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include "../hybriddomain/doc/userfuncs.h"\n\n'
        outputStr += self.generator.generateAllDefinitions()
        outputStr += self.generator.generateInitials()
        
        totalArrWithFunctionNames = list()
        functionMaps = []
        for blockNumber, block in enumerate(self.generator.blocks):
            systemsForCentralFuncs, numsForSystems, totalBCondLst, totalInterconnectLst, blockFunctionMap = self.generator.getBlockInfo(block, blockNumber)
            cf, arrWithFunctionNames = self.generator.generateCentralFunctionCode(block, blockNumber, systemsForCentralFuncs, numsForSystems)
            bf = self.generator.generateBoundsAndIcs(blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst)
            
            totalArrWithFunctionNames.append(arrWithFunctionNames)
            functionMaps.append(blockFunctionMap)
            outputStr += cf + bf
            
        final = self.generator.generateGetBoundFuncArray(totalArrWithFunctionNames)
        outputStr += final
         
        return outputStr , functionMaps

class BoundCondition:
    def __init__(self, values, btype, side, ranges, boundNumber, equationNumber, equation, funcName):
        self.name = "BoundCondition"
        self.values = values
        self.btype = btype
        self.side = side
        self.ranges = ranges
        self.boundNumber = boundNumber
        self.equationNumber = equationNumber
        self.equation = equation
        self.funcName = funcName
         
    def createSpecialProperties(self, mathParser, params, indepVars):
# Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
# boundaryCoordinates отличается от ranges тем, что ranges -- это то как задал границу юзер,
# а boundaryCoordinates -- координаты крайних точек границы в геометрическом смысле 
        self.parsedValues = list()
        for value in self.values:
            self.parsedValues.append(mathParser.parseMathExpression(value, params, indepVars))
        
        self.unknownVars = mathParser.getVariableList(self.equation.system)    
        self.parsedEquation = list()
        for equat in self.equation.system:
            self.parsedEquation.extend([mathParser.parseMathExpression(equat, self.unknownVars, params, self.equation.vars)])

class Connection:
    def __init__(self, firstIndex, secondIndex, side, ranges, equationNumber, equation, funcName):
        self.name = "Connection"
        self.firstIndex = firstIndex
        self.secondIndex = secondIndex
        self.side = side
        self.ranges = ranges
        self.equationNumber = equationNumber
        self.equation = equation
        self.funcName = funcName
    
    def createSpecialProperties(self, mathParser, params):
# Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
# boundaryCoordinates отличается от ranges тем, что ranges -- это то как задал границу юзер,
# а boundaryCoordinates -- координаты крайних точек границы в геометрическом смысле 
        self.unknownVars = mathParser.getVariableList(self.equation.system)    
        self.parsedEquation = list()
        for equat in self.equation.system:
            self.parsedEquation.extend([mathParser.parseMathExpression(equat, self.unknownVars, params, self.equation.vars)])

class InterconnectRegion:
    def __init__(self, firstIndex, secondIndex, side, stepAlongSide, lenBetweenStartOfBlockSideAndStartOfConnection, lenOfConnection, xfrom, xto, yfrom, yto, secondaryBlockNumber):
        self.firstIndex = firstIndex
        self.secondIndex = secondIndex
        self.side = side
        self.stepAlongSide = stepAlongSide
        self.lenBetweenStartOfBlockSideAndStartOfConnection = lenBetweenStartOfBlockSideAndStartOfConnection
        self.lenOfConnection = lenOfConnection
        self.xfrom = xfrom
        self.xto = xto
        self.yfrom = yfrom
        self.yto = yto
        self.secondaryBlockNumber = secondaryBlockNumber
    
class abstractGenerator(object):
# Генерирует выходную строку для записи в файл
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamsIndex):
        self.equations = equations
        self.blocks = blocks
        self.initials = initials
        self.bounds = bounds
        self.interconnects = interconnects
        self.gridStep = gridStep
        
        self.userIndepVars = equations[0].vars
        self.defaultIndepVars = ['x','y','z']
        
        self.params = params
        self.paramValues = paramValues
        self.defaultParamsIndex = defaultParamsIndex

    def generateAllDefinitions(self):
# allBlockSizeLists = [[Block0SizeX, Block0SizeY, Block0SizeZ], [Block1SizeX, Block1SizeY, Block1SizeZ]}, ...]
# allBlockOffsetList = [[Block0OffsetX, Block0OffsetY, Block0OffsetZ], [Block1OffsetX, Block1OffsetY, Block1OffsetZ]}, ...]
# cellsizeList= [Block0CELLSIZE, Block1CELLSIZE, ...]
# allStrideLists --- это список strideОВ для каждого блока: [[block0StrideX,block0StrideY,block0StrideZ],[block1StrideX,Y,Z], ...]
# allCountLists --- аналогичный список, только для countОВ
# DList = [DX,DY,DZ]
# D2List = [DX2,DY2,DZ2]
# DM2List = [DXM2,DYM2,DZM2]
#         Требуем, чтобы длины всех массивов были одинаковы
        if len(self.gridStep) != len(self.defaultIndepVars):
            raise AttributeError("A list 'gridStep' should be consist of values for ALL independent variables!")
        a = set({len(self.allBlockSizeList), len(self.cellsizeList), len(self.allBlockOffsetList)})
        if len(a) != 1:
            raise AttributeError("Number of elements in 'allBlockSizeLists', 'cellsizeList' and 'allBlockOffsetList' should be the same!")
        
        D2List = list([])
        DM1List = list([])
        DM2List = list([])
        for d in self.gridStep:
            d2 = d * d
            D2List.append(d2)
            DM1List.append(round(1 / d))
            DM2List.append(round(1 / d2))
        
#         Вычисляем все страйды и каунты    
        allStrideLists = list([])
        allCountLists = list([])
        for blockNumber, blockSizeList in enumerate(self.allBlockSizeList):
            strideList = list([])
            countList = list([])
            for (d, sizeForIndepVar) in zip(self.gridStep, blockSizeList):
                countList.append(int(sizeForIndepVar / d))
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
        for (indepVar, d, d2, dm1, dm2) in zip(self.defaultIndepVars, self.gridStep, D2List, DM1List, DM2List):
            definitions.append('#define D' + indepVar.upper() + ' ' + str(d) + '\n')
            definitions.append('#define D' + indepVar.upper() + '2 ' + str(d2) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M1 ' + str(dm1) + '\n')
            definitions.append('#define D' + indepVar.upper() + 'M2 ' + str(dm2) + '\n')
        for blockNumber,(strideList, countList, offsetList, cellsize) in enumerate(zip(allStrideLists, allCountLists, self.allBlockOffsetList, self.cellsizeList)):
            definitions.append('\n#define Block' + str(blockNumber) + 'CELLSIZE ' + str(cellsize) + '\n\n')
            for (indepVar, stride, count, offset) in zip(self.defaultIndepVars, strideList, countList, offsetList):
                definitions.append('#define Block' + str(blockNumber) + 'Stride' + indepVar.upper() + ' ' + str(stride) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Count' + indepVar.upper() + ' ' + str(count) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Offset' + indepVar.upper() + ' ' + str(offset) + '\n')
        definitions.append("\n#define PAR_COUNT " + str(len(self.params)) + "\n\n")

        return ''.join(definitions)
                   
    def generateParamFunction(self):
        output = list(["void initDefaultParams(double** pparams, int* pparamscount){\n"])
        if len(self.paramValues) > 0:
            paramCount = len(self.params)
            paramValuesCount = len(self.paramValues[self.defaultParamsIndex])
            if paramCount != paramValuesCount:
                raise AttributeError("Count of parameter values is not corresponds to count of parameters!")
            output.append("\t*pparamscount = PAR_COUNT;\n")
            output.append("\t*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);\n")
            
            for index,param in enumerate(self.params):
                output.append("\t(*pparams)[" + str(index) + "] = " + str(self.paramValues[self.defaultParamsIndex][param]) + ";\n")
        
            output.append("}\n\nvoid releaseParams(double *params){\n\tfree(params);\n}\n\n")
        else:
            output.append("}\n\nvoid releaseParams(double *params){}\n\n")
        
        return ''.join(output)
    
    def generateAllPointInitials(self):
#         Генерирует все точечные начальные функции и возвращает строку из них; возвращает массив, содержащий имена начальных функций и
#         массив, содержащий имена граничных функций Дирихле.
#         Индекс в этом массиве имени каждой сгенерированной начальной функции совпадает с индексом соответствующего начального условия
#         в массиве файла .json
#         Все для начальных условий
#         countOfEquations = len(self.system)
        parser = MathExpressionParser()
        allFunctions = list()
        listWithInitialFunctionNames = list()
        for initialNumber, initial in enumerate(self.initials):
            pointFunction = list()
            valueList = initial.values
#             if len(valueList) != countOfEquations:
#                 raise AttributeError("Component's count of some initial condition is not corresponds to component's count of unknown vector-function!")      
            name = "Initial"+str(initialNumber)
            listWithInitialFunctionNames.append(name)
            pointFunction.append("void " + name + "(double* cellstart, double x, double y, double z){\n")
            
            indepVarsForInitialFunction = self.userIndepVars + ['t']
            for k,value in enumerate(valueList):
                parsedInitial = parser.parseMathExpression(value, self.params, indepVarsForInitialFunction)
                newValue = generateCodeForMathFunction(parsedInitial, self.userIndepVars, indepVarsForInitialFunction)
                pointFunction.append("\tcellstart[" + str(k) + "] = " + newValue + ";\n")
            pointFunction.append("}\n\n")
            allFunctions.append(''.join(pointFunction))
#         Все для условий Дирихле
        listWithDirichletFunctionNames = list()    
        for boundNumber, bound in enumerate(self.bounds):
            if bound.btype == 0:
                pointFunction = list()
                valueList = bound.values
#                 if len(valueList) != countOfEquations:
#                     raise AttributeError("Component's count of some boundary condition is not corresponds to component's count of unknown vector-function!")      
                name = "DirichletInitial" + str(boundNumber)
                listWithDirichletFunctionNames.append(name)
                pointFunction.append("void " + name + "(double* cellstart, double x, double y, double z){\n")
                
                indepVarsForInitialFunction = self.userIndepVars + ['t']
                for k,value in enumerate(valueList):
                    parsedInitial = parser.parseMathExpression(value, self.params, indepVarsForInitialFunction)
                    parsedInitialAfterReplacing = self.replaceTimeToZeroInInitialCondition(parsedInitial)
                    newValue = generateCodeForMathFunction(parsedInitialAfterReplacing, self.userIndepVars, indepVarsForInitialFunction)
                    pointFunction.append("\tcellstart[" + str(k) + "] = " + newValue + ";\n")
                pointFunction.append("}\n\n")
                allFunctions.append(''.join(pointFunction))
            else:
                listWithDirichletFunctionNames.append("empty")
        return ''.join(allFunctions), listWithInitialFunctionNames, listWithDirichletFunctionNames
    
    def replaceTimeToZeroInInitialCondition(self, DirichletConditionForParsing):
#         Заменяет в условии Дирихле, которое хотим сделать начальным условием, переменную t на 0.0;
#         DirichletConditionForParsing -- функция, в которой выполняется замена. Она здесь -- в виде массива лексем уже.
        operations = ['+','-','*','/']
        prevOperationsAndBoundaries = operations + ['(']
        postOperationsAndBoundaries = operations + [')']
        lastIndexInList = len(DirichletConditionForParsing) - 1
        for idx,element in enumerate(DirichletConditionForParsing):
            if element != 't':
                continue
            doReplace = False
#                 Если в строке стоит лишь 't'
            if lastIndexInList == 0:
                return '0.0'
            if idx == 0:
                if len(DirichletConditionForParsing[idx + 1]) == 1 and DirichletConditionForParsing[idx + 1] in operations:
                    doReplace = True
                elif len(DirichletConditionForParsing[idx + 1]) != 1 and DirichletConditionForParsing[idx + 1][0] == '^':
                    doReplace = True
            elif idx == lastIndexInList and DirichletConditionForParsing[idx - 1] in operations:
                doReplace = True
            else:
                prevElement = DirichletConditionForParsing[idx - 1]
                postElement = DirichletConditionForParsing[idx + 1]
                if prevElement in prevOperationsAndBoundaries or postElement in postOperationsAndBoundaries:
                    doReplace = True
                elif len(postElement) > 1 and postElement[0] == '^':
                    doReplace = True
            if doReplace:
                DirichletConditionForParsing.pop(idx)
                DirichletConditionForParsing.insert(idx, '0.0')
        
        return DirichletConditionForParsing
    
    def genCommonPartForFillInitValFunc(self, block, blockNumber, totalCountOfInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames):
# Функция генерирует часть функции-заполнителя, общую для блоков каждой размерности
# Для данного блока определяется список индексов начальных функций в массиве listWithInitialFunctionNames
        defaultInitialIndex = block.defaultInitial
        listOfInitialIndices = list([defaultInitialIndex])
        for initialRegion in block.initialRegions:
            if initialRegion.initialNumber >= totalCountOfInitials:
                raise AttributeError("Number of initial condition in some initial region of some block shouldn't be greater or equal to count of initials!")
            if initialRegion.initialNumber != defaultInitialIndex:
                listOfInitialIndices.append(initialRegion.initialNumber)
        countOfInitialsForBlock = len(listOfInitialIndices)
# Для данного блока определяется список индексов функций Дирихле в массиве listWithDirichletFunctionNames            
        setOfDirichletIndices = set([])
        countOfBoundaries = len(self.bounds)
        for boundRegion in block.boundRegions:
            boundNumber = boundRegion.boundNumber
            if boundNumber >= countOfBoundaries:
                raise AttributeError("In some of bound regions the value of bound number greater or equal to count of boundaries!")
            if self.bounds[boundNumber].btype == 0 and boundNumber not in setOfDirichletIndices:
                setOfDirichletIndices.add(boundNumber)
        countOfDirichletForBlock = len(setOfDirichletIndices)
# Генерируется начало самой функции-заполнителя.
        partOfFillFunction = list()
        strBlockNum = str(blockNumber)
        signature = "void Block" + strBlockNum + "FillInitialValues(double* result, unsigned short int* initType){\n"
        partOfFillFunction.append(signature)
        
        partOfFillFunction.append("\tinitfunc_ptr_t initFuncArray[" + str(countOfInitialsForBlock + countOfDirichletForBlock) + "];\n")
#             Создаем заполнение начальными функциями
        for num, idx in enumerate(listOfInitialIndices):
            number = str(num)
            partOfFillFunction.append("\tinitFuncArray[" + number + "] = " + listWithInitialFunctionNames[idx] + ";\n")
#             Создаем заполнение функциями Дирихле
        for num1, idx1 in enumerate(setOfDirichletIndices):
            number1 = str(countOfInitialsForBlock + num1)
            partOfFillFunction.append("\tinitFuncArray[" + number1 + "] = " + listWithDirichletFunctionNames[idx1] + ";\n")
        return ''.join(partOfFillFunction)
    
    def generateGetInitFuncArray(self):
        countOfBlocks = len(self.blocks)
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
    
    def generateCentralFunctionCode(self, block, blockNumber, equationsList, numsForEquats):
#         defaultIndepVars отличается лишь количеством элементов userIndepVars, т.к. считаем, что переменные могут называться только x,y,z.
        function = list([])
        function.extend(['\n//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
        strideList = list([])
#         Здесь используется defaultIndepVrbls, потому что договорились генерировать сигнатуры функций с одинаковым количеством параметров.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        
        parser = MathExpressionParser()
        arrWithFuncNames = list()
        for num, equation in enumerate(equationsList): 
            function.extend(['//'+str(num)+' central function for '+str(len(self.userIndepVars))+'d model for block with number ' + str(blockNumber) + '\n'])    
            name = 'Block' + str(blockNumber) + 'CentralFunction' + str(numsForEquats[num])
            arrWithFuncNames.append(name)
            function.extend(self.generateFunctionSignature(blockNumber, name, strideList))
            
            variables = parser.getVariableList(equation.system)
#         Во все парсеры необходимо передавать именно userIndepVars!
            b = RHSCodeGenerator()
            for i, equationString in enumerate(equation.system):
                equationRightHandSide = parser.parseMathExpression(equationString, variables, self.params, self.userIndepVars)
                function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equationRightHandSide, self.userIndepVars, variables, self.params)])
            function.extend(['}\n\n'])
        
        return ''.join(function), arrWithFuncNames

    def generateFunctionSignature(self, blockNumber, name, strideList):
        signatureStart = 'void ' + name + '(double* result, double* source, double t,'
        signatureMiddle = ' int idx' + self.defaultIndepVars[0].upper() + ','
#         Делаем срез нулевого элемента, т.к. его уже учли
        for indepVar in self.defaultIndepVars[1:]:
            signatureMiddle = signatureMiddle + ' int idx' + indepVar.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'
        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ( idx' + self.defaultIndepVars[0].upper()
#         Опять срезаем нулевой элемент, т.к. его тоже уже учли
        changedStrideList = strideList[1:]
        for i,indepVar in enumerate(self.defaultIndepVars[1:]):
            idx = idx + ' + idx' + indepVar.upper() + ' * ' + changedStrideList[i]
        idx = idx + ') * Block' + str(blockNumber) + 'CELLSIZE;\n'
        
        return list([signature,idx])
    
    def createACL(self, totalBCondLst, parser):
# Парсит краевые условия и создает список условий на углы (angleCondList) 
        for bCondListForSide in totalBCondLst:  
            for bCond in bCondListForSide:
                indepVarsForBoundaryFunction = list(self.userIndepVars)
                indepVarsForBoundaryFunction.remove(self.userIndepVars[bCond.side // 2])
                indepVarsForBoundaryFunction.extend(['t'])
                
                if not isinstance(bCond, Connection):
                    bCond.createSpecialProperties(parser, self.params, indepVarsForBoundaryFunction)
                else:
                    bCond.createSpecialProperties(parser, self.params)
# Создание списка условий на углы. В него входят условия с уже распарсенными значениями        
        condCntOnS2 = len(totalBCondLst[0])
        condCntOnS3 = len(totalBCondLst[1])
        condCntOnS0 = len(totalBCondLst[2])
        condCntOnS1 = len(totalBCondLst[3])
        angleCondList = [[totalBCondLst[0][0], totalBCondLst[2][0]], [totalBCondLst[0][condCntOnS2-1], totalBCondLst[3][0]],
                         [totalBCondLst[1][0], totalBCondLst[2][condCntOnS0-1]], [totalBCondLst[1][condCntOnS3-1], totalBCondLst[3][condCntOnS1-1]]]
#         if isinstance(totalBCondLst[0][0], Connection):
#             angleCondList.append([totalBCondLst[0][0]])
#         elif isinstance(totalBCondLst[2][0], Connection):
#             angleCondList.append([totalBCondLst[2][0]])
#         else:
#             angleCondList.append([totalBCondLst[0][0], totalBCondLst[2][0]])
#             
#         if isinstance(totalBCondLst[0][condCntOnS2-1], Connection):
#             angleCondList.append([totalBCondLst[0][condCntOnS2-1]])
#         elif isinstance(totalBCondLst[3][0], Connection):
#             angleCondList.append([totalBCondLst[3][0]])
#         else:
#             angleCondList.append([totalBCondLst[0][condCntOnS2-1], totalBCondLst[3][0]])
#             
#         if isinstance(totalBCondLst[1][0], Connection):
#             angleCondList.append([totalBCondLst[1][0]])
#         elif isinstance(totalBCondLst[2][condCntOnS0-1], Connection):
#             angleCondList.append([totalBCondLst[2][condCntOnS0-1]])
#         else:
#             angleCondList.append([totalBCondLst[1][0], totalBCondLst[2][condCntOnS0-1]])
#             
#         if isinstance(totalBCondLst[1][condCntOnS3-1], Connection):
#             angleCondList.append([totalBCondLst[1][condCntOnS3-1]])
#         elif isinstance(totalBCondLst[3][condCntOnS1-1], Connection):
#             angleCondList.append([totalBCondLst[3][condCntOnS1-1]])
#         else:
#             angleCondList.append([totalBCondLst[1][condCntOnS3-1], totalBCondLst[3][condCntOnS1-1]])
        return angleCondList
    
    def setDefault(self, blockNumber, side, equation, equationNum):
        systemLen = len(equation.system)
        funcName = "Block" + str(blockNumber) + "DefaultNeumann__Bound" + str(side) + "_Eqn" + str(equationNum)
        return systemLen * ['0.0'], 1, -1, funcName
    
    def setDirichletOrNeumann(self, bRegion, blockNumber, side, equationNum):
        boundNumber = bRegion.boundNumber
        btype = self.bounds[boundNumber].btype
        if btype == 0:
            funcName = "Block" + str(blockNumber) + "Dirichlet__Bound" + str(side) + "_" + str(boundNumber) + "_Eqn" + str(equationNum)
            outputValues = list(self.bounds[boundNumber].derivative)
        elif btype == 1:
            funcName = "Block" + str(blockNumber) + "Neumann__Bound" + str(side) + "_" + str(boundNumber) + "_Eqn" + str(equationNum)
            outputValues = list(self.bounds[boundNumber].values)
#                 Особенность Неймановского условия
            if side == 0 or side == 2:
                for idx, value in enumerate(outputValues):
                    outputValues.pop(idx)
                    outputValues.insert(idx, '-(' + value + ')')
        values = list(outputValues)
        return values, btype, boundNumber, funcName
    
    def generateDirichlet(self, blockNumber, name, boundaryCondition):
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function = self.generateFunctionSignature(blockNumber, name, strideList)
#         А здесь используем userIndepVariables.        
        indepVarValueList = list([])
        for indepVar in self.userIndepVars:
            indepVarValueList.extend(['idx' + indepVar.upper()])
        indepVarValueList.extend(['t'])
        
        for i,boundary in enumerate(boundaryCondition.parsedValues):
            boundaryExpression = generateCodeForMathFunction(boundary, self.userIndepVars, indepVarValueList)
            result = '\t result[idx + ' + str(i) + '] = ' + boundaryExpression + ';\n'
            function.append(result)
        function.append('}\n')
        return ''.join(function)
        
    def generateNeumannOrInterconnect(self, blockNumber, name, parsedEquationsList, unknownVars, pBCL): 
#         parsedBoundaryConditionList --- это список, содержащий от 1 до 3 элементов
#         parsedEquationsList --- список, элементы которого --- распарсенные правые части всех уравнений
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        
        function = self.generateFunctionSignature(blockNumber, name, strideList)
#         А здесь используем userIndepVariables.
        b = RHSCodeGenerator()
        for i, equation in enumerate(parsedEquationsList):
#             Для трехмерного случая все должно усложниться в следующей команде
            function.extend([b.generateRightHandSideCode(blockNumber, unknownVars[i], equation, self.userIndepVars, unknownVars, self.params, pBCL)])
        function.extend(['}\n'])
        return ''.join(function)
        
    def generateGetBoundFuncArray(self, totalArrWithFunctionNames):
        intro = "\n//===================================FILL FUNCTIONS===========================//\n\n"
        output = list(intro)
        countOfBlocks = len(self.blocks)
        for blockNumber in range(0, countOfBlocks):
            arrWithFunctionNames = totalArrWithFunctionNames[blockNumber]
            output.append("void getBlock" + str(blockNumber) + "BoundFuncArray(func_ptr_t** ppBoundFuncs){\n")
            output.append("\tfunc_ptr_t* pBoundFuncs = *ppBoundFuncs;\n")
            output.append("\tpBoundFuncs = (func_ptr_t*) malloc( " + str(len(arrWithFunctionNames)) + " * sizeof(func_ptr_t) );\n")
            output.append("\t*ppBoundFuncs = pBoundFuncs;\n\n")
            for i,funcName in enumerate(arrWithFunctionNames):
                index = str(i)
                output.append("\tpBoundFuncs[" + index + "] = " + funcName + ";\n")
            output.append("}\n\n")
            
        output.append("void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx){\n")
        if countOfBlocks == 1:
            output.append("\tgetBlock0BoundFuncArray(ppBoundFuncs);\n")
        else:
            for blockNumber in range(0, countOfBlocks):
                output.append("\tif (blockIdx == " + str(blockNumber) + ")\n\t\tgetBlock" + str(blockNumber) + "BoundFuncArray(ppBoundFuncs);\n")
        output.append("}\n\n")
        output.append("void releaseFuncArray(func_ptr_t* BoundFuncs){\n\tfree(BoundFuncs);\n}\n\n")
        
        return ''.join(output)
    
class generator1D(abstractGenerator):
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(generator1D,self).__init__(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(equations[block.defaultEquation].system))
            self.allBlockOffsetList.append([block.offsetX, 0, 0])
            self.allBlockSizeList.append([block.sizeX, 0, 0])
    
    def generateInitials(self):
#         initials --- массив [{"Name": '', "Values": []}, {"Name": '', "Values": []}]
        output = list(["//===================PARAMETERS==========================//\n\n"])
        output.append(self.generateParamFunction())
        output.append("//===================INITIAL CONDITIONS==========================//\n\n")

        pointInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames = self.generateAllPointInitials()
        output.append(pointInitials)
        output.append(self.generateFillInitValFuncsForAllBlocks(listWithInitialFunctionNames, listWithDirichletFunctionNames))
        output.append(self.generateGetInitFuncArray())
        
        return ''.join(output)  
    
    def generateFillInitValFuncsForAllBlocks(self, listWithInitialFunctionNames, listWithDirichletFunctionNames):
#         Для каждого блока создает функцию-заполнитель с именем BlockIFillInitialValues (I-номер блока)
        totalCountOfInitials = len(listWithInitialFunctionNames)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
            strBlockNum = str(blockNumber)
            fillFunction = self.genCommonPartForFillInitValFunc(block, blockNumber, totalCountOfInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames)
            fillFunction += "\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n"
            fillFunction += "\t\tint idx = idxX;\n" #*Block" + strBlockNum + "CELLSIZE
            fillFunction += "\t\tint type = initType[idx];\n"
            fillFunction += "\t\tinitFuncArray[type](result+idx*Block" + strBlockNum + "CELLSIZE, Block" + strBlockNum + "OffsetX + idxX*DX, 0, 0);\n\t}\n"
            fillFunction += "}\n\n"
            allFillFunctions.append(fillFunction)
        return ''.join(allFillFunctions)
    
    def getBlockInfo(self, block, blockNumber):
        systemsForCentralFuncs = []
        numsForSystems = []
        blockFuncMap = {'center': []}
        reservedSpace = 0
        for eqRegion in block.equationRegions:
            reservedSpace += eqRegion.xto - eqRegion.xfrom
            cond = eqRegion.xfrom == eqRegion.xto and (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX)
            if eqRegion.equationNumber not in numsForSystems and not cond:
                systemsForCentralFuncs.append(self.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)
            if not cond:
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber), eqRegion.xfrom, eqRegion.xto])
        if block.sizeX > reservedSpace:
            systemsForCentralFuncs.append(self.equations[block.defaultEquation])
            blockFuncMap.update({'center_default': len(numsForSystems)})
            numsForSystems.append(block.defaultEquation)
        
        totalBCondLst = list()
        sides = [0,1]
        for side in sides:
            totalBCondLst.append(self.createListOfBCondsForSide(block, blockNumber, side))
            
        totalInterconnectLst = self.createListOfInterconnects(block, blockNumber)
        
        return systemsForCentralFuncs, numsForSystems, totalBCondLst, totalInterconnectLst, blockFuncMap
    
    def createListOfBCondsForSide(self, block, blockNumber, side):
        if side == 0:
            Range = 0.0
            coord = lambda region: region.xfrom
        else:
            Range = block.sizeX
            coord = lambda region: region.xto 
            
        for eqRegion in block.equationRegions:
            if coord(eqRegion) == Range:
                equationNum = eqRegion.equationNumber
                break
        else:
            equationNum = block.defaultEquation
        equation = self.equations[equationNum]
        for bRegion in block.boundRegions:
            if bRegion.side == side:
                values, btype, boundNumber, funcName = self.setDirichletOrNeumann(bRegion, blockNumber, side, equationNum)
                break
        else:
            values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
        return BoundCondition(values, btype, side, [], boundNumber, equationNum, equation, funcName)
    
    def createListOfInterconnects(self, block, blockNumber):
        icsForBlock = []
        for iconn in self.interconnects:
            #Если блок зациклен.
            if iconn.block1 == blockNumber and iconn.block2 == blockNumber:
                Range1 = (iconn.block1Side == 1) * block.sizeX
                Range2 = (iconn.block2Side == 1) * block.sizeX
                coord1 = lambda region: (iconn.block1Side == 0) * region.xfrom + (iconn.block1Side == 1) * region.xto
                coord2 = lambda region: (iconn.block2Side == 0) * region.xfrom + (iconn.block2Side == 1) * region.xto
                for eqRegion in block.equationRegions:
                    if coord1(eqRegion) == Range1:
                        equationNum1 = eqRegion.equationNumber
                        break
                else:
                    equationNum1 = block.defaultEquation
                for eqRegion in block.equationRegions:
                    if coord2(eqRegion) == Range2:
                        equationNum2 = eqRegion.equationNumber
                        break
                else:
                    equationNum2 = block.defaultEquation
                equation1 = self.equations[equationNum1]
                equation2 = self.equations[equationNum2]
                funcName1 = "Block" + str(blockNumber) + "Interconnect__Side" + str(iconn.block1Side) + "_Eqn" + str(equationNum1)
                funcName2 = "Block" + str(blockNumber) + "Interconnect__Side" + str(iconn.block2Side) + "_Eqn" + str(equationNum2)
                icsForBlock.append(Connection(0, '0', iconn.block2Side, [], equationNum2, equation2, funcName2))
                icsForBlock.append(Connection(1, '0', iconn.block1Side, [], equationNum1, equation1, funcName1))
                continue
            #Если соединяются несколько блоков
            elif iconn.block1 == blockNumber and iconn.block2 != blockNumber:
                side = iconn.block1Side
            elif iconn.block2 == blockNumber and iconn.block1 != blockNumber:
                side = iconn.block2Side
            else:
                continue
            firstIndex = len(icsForBlock)
            Range = (side == 1) * block.sizeX
            coord = lambda region: (side == 0) * region.xfrom + (side == 1) * region.xto
#             if side == 0:
#                 Range = 0.0
#                 coord = lambda region: region.xfrom
#             else:
#                 Range = block.sizeX
#                 coord = lambda region: region.xto 
#                 
            for eqRegion in block.equationRegions:
                if coord(eqRegion) == Range:
                    equationNum = eqRegion.equationNumber
                    break
            else:
                equationNum = block.defaultEquation
            equation = self.equations[equationNum]
            funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(side) + "_Eqn" + str(equationNum)
            icsForBlock.append(Connection(firstIndex, '0', side, [], equationNum, equation, funcName))
        return icsForBlock
                
    def generateBoundsAndIcs(self, blockNumber, arrWithFunctionNames, blockFunctionMap, bCondLst, icsList):
        #  ***x->
        #  *  
        #  |  ---side 2---
        #  y  |          |
        #     s          s
        #     i          i
        #     d          d
        #     e          e
        #     0          1
        #     |          |
        #     ---side 3---  
        parser = MathExpressionParser()
#         self.createACL(bCondLst, parser)
        intro = '\n//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'
        outputStr = [intro]      
        
        for condition in bCondLst:
            for iconn in icsList:
                if iconn.side == condition.side:
                    outputStr.append(self.generateInterconnect(iconn, parser, blockNumber, arrWithFunctionNames, blockFunctionMap))
                    break
            else:
                outputStr.append(self.generateBound(condition, parser, blockNumber, arrWithFunctionNames, blockFunctionMap))
        return ''.join(outputStr)
    
    def generateBound(self, condition, parser, blockNumber, arrWithFunctionNames, blockFunctionMap):
        indepVarsForBoundaryFunction = list(self.userIndepVars)
        indepVarsForBoundaryFunction.remove(self.userIndepVars[condition.side // 2])
        indepVarsForBoundaryFunction.extend(['t'])
        
        condition.createSpecialProperties(parser, self.params, indepVarsForBoundaryFunction)
        boundaryName = determineNameOfBoundary(condition.side)
        sideName = "side"+str(condition.side)
        outputStr = '//Boundary condition for boundary ' + boundaryName + '\n'
        if condition.btype == 0:
            outputStr += self.generateDirichlet(blockNumber, condition.funcName, condition)
        else:
            pBCL = [condition]
            outputStr += self.generateNeumannOrInterconnect(blockNumber, condition.funcName, condition.parsedEquation, condition.unknownVars, pBCL)
        idx = len(arrWithFunctionNames)
        blockFunctionMap.update({sideName: idx})
        arrWithFunctionNames.append(condition.funcName)
        return outputStr
    
    def generateInterconnect(self, iconn, parser, blockNumber, arrWithFunctionNames, blockFunctionMap):
        iconn.createSpecialProperties(parser, self.params)
        boundaryName = determineNameOfBoundary(iconn.side)
        sideName = "side"+str(iconn.side)
        outputStr = '//Interconnect for block ' + str(blockNumber) + ' for boundary ' + boundaryName + '\n'
        pBCL = [iconn]
        outputStr += self.generateNeumannOrInterconnect(blockNumber, iconn.funcName, iconn.parsedEquation, iconn.unknownVars, pBCL)
        idx = len(arrWithFunctionNames)
        blockFunctionMap.update({sideName: idx})
        arrWithFunctionNames.append(iconn.funcName)
        return outputStr
    
class generator2D(abstractGenerator):
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(generator2D,self).__init__(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(equations[block.defaultEquation].system))
            self.allBlockOffsetList.append([block.offsetX, block.offsetY, 0])
            self.allBlockSizeList.append([block.sizeX, block.sizeY, 0])
            self.__createBlockIcsRegions(block)
    
    def __createBlockIcsRegions(self, block):
        blockNumber = self.blocks.index(block)
        icsRegions = []
        firstIndex = 0
        for interconnect in self.interconnects:
            if interconnect.block1 == blockNumber and interconnect.block2 == blockNumber:
                icsRegions.append(self.__createIcRegion(interconnect.block2Side, block, self.blocks[interconnect.block1], firstIndex))
                firstIndex += 1
                icsRegions.append(self.__createIcRegion(interconnect.block1Side, block, self.blocks[interconnect.block2], firstIndex))
                firstIndex += 1
            elif interconnect.block1 == blockNumber and interconnect.block2 != blockNumber:
                icsRegions.append(self.__createIcRegion(interconnect.block1Side, block, self.blocks[interconnect.block2], firstIndex))
                firstIndex += 1
            elif interconnect.block2 == blockNumber and interconnect.block1 != blockNumber:
                icsRegions.append(self.__createIcRegion(interconnect.block2Side, block, self.blocks[interconnect.block1], firstIndex))
                firstIndex += 1
        block.interconnectRegions = icsRegions
                
    def __createIcRegion(self, mainBlockSide, mainBlock, secBlock, firstIndex):
        if mainBlockSide == 0:
            xfrom = mainBlock.offsetX
            xto = mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[0]
        elif mainBlockSide == 1:
            xfrom = mainBlock.offsetX + mainBlock.sizeX
            xto = mainBlock.offsetX + mainBlock.sizeX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[0]
        elif mainBlockSide == 2:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = mainBlock.offsetY
            yto = mainBlock.offsetY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[1]
        else:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = mainBlock.offsetY + mainBlock.sizeY
            yto = mainBlock.offsetY + mainBlock.sizeY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[1]
        return InterconnectRegion(firstIndex, secondIndex, mainBlockSide, stepAlongSide, someLen, lenOfConnection, xfrom, xto, yfrom, yto, self.blocks.index(secBlock))
    
    def generateInitials(self):
#         initials --- массив [{"Name": '', "Values": []}, {"Name": '', "Values": []}]
        output = list(["//===================PARAMETERS==========================//\n\n"])
        output.append(self.generateParamFunction())
        output.append("//===================INITIAL CONDITIONS==========================//\n\n")

        pointInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames = self.generateAllPointInitials()
        output.append(pointInitials)
        output.append(self.generateFillInitValFuncsForAllBlocks(listWithInitialFunctionNames, listWithDirichletFunctionNames))
        output.append(self.generateGetInitFuncArray())
        
        return ''.join(output)  
    
    def generateFillInitValFuncsForAllBlocks(self, listWithInitialFunctionNames, listWithDirichletFunctionNames):
#         Для каждого блока создает функцию-заполнитель с именем BlockIFillInitialValues (I-номер блока)
        totalCountOfInitials = len(listWithInitialFunctionNames)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
            strBlockNum = str(blockNumber)
            fillFunction = self.genCommonPartForFillInitValFunc(block, blockNumber, totalCountOfInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames)
            fillFunction += "\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n"
            fillFunction += "\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n"
            fillFunction += "\t\t\tint idx = idxY*Block" + strBlockNum + "CountX + idxX;\n"
            fillFunction += "\t\t\tint type = initType[idx];\n"
            fillFunction += "\t\t\tinitFuncArray[type](result+idx*Block" + strBlockNum + "CELLSIZE, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, 0);\n\t\t}\n"
            fillFunction += "}\n\n"
            allFillFunctions.append(fillFunction)
        return ''.join(allFillFunctions)
     
    def getBlockInfo(self, block, blockNumber):
        systemsForCentralFuncs = []
        numsForSystems = []
        blockFuncMap = {'center': []}
        blockSquare = block.sizeX * block.sizeY
        reservedSquare = 0
        for eqRegion in block.equationRegions:
            cond1 = eqRegion.xfrom == eqRegion.xto and (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX)
            cond2 = eqRegion.yfrom == eqRegion.yto and (eqRegion.yto == 0.0 or eqRegion.yto == block.sizeY)
            reservedSquare += RectSquare([eqRegion.xfrom, eqRegion.xto], [eqRegion.yfrom, eqRegion.yto])
            if eqRegion.equationNumber not in numsForSystems and not cond1 and not cond2:
                systemsForCentralFuncs.append(self.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)
            if not cond1 and not cond2:
                x1 = eqRegion.xfrom
                x2 = eqRegion.xto
                y1 = eqRegion.yfrom
                y2 = eqRegion.yto
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber), x1, x2, y1, y2])
        if blockSquare > reservedSquare:
            systemsForCentralFuncs.append(self.equations[block.defaultEquation])
            blockFuncMap.update({'center_default': len(numsForSystems)})
            numsForSystems.append(block.defaultEquation)
        
        totalBCondLst = list()
        sides = [2,3,0,1]
        for side in sides:
            totalBCondLst.append(self.createListOfBCondsForSide(block, blockNumber, side))
        
        return systemsForCentralFuncs, numsForSystems, totalBCondLst, [], blockFuncMap
    
    def createListOfBCondsForSide(self, block, blockNumber, side):
        if side == 2:
            cellLen = self.gridStep[1]
            sideMaxRange = block.sizeX
            sideMinRange = 0.0
            currentSideValue = 0.0
            sideIndicator = lambda eqRegion: eqRegion.yfrom
            stepFrom = lambda eqRegion: eqRegion.xfrom
            stepTo = lambda eqRegion: eqRegion.xto
        elif side == 3:
            cellLen = self.gridStep[1]
            sideMaxRange = block.sizeX
            sideMinRange = 0.0
            currentSideValue = block.sizeY
            sideIndicator = lambda eqRegion: eqRegion.yto
            stepFrom = lambda eqRegion: eqRegion.xfrom
            stepTo = lambda eqRegion: eqRegion.xto
        elif side == 0:
            cellLen = self.gridStep[0]
            sideMaxRange = block.sizeY
            sideMinRange = 0.0
            currentSideValue = 0.0
            sideIndicator = lambda eqRegion: eqRegion.xfrom
            stepFrom = lambda eqRegion: eqRegion.yfrom
            stepTo = lambda eqRegion: eqRegion.yto
        elif side == 1:
            cellLen = self.gridStep[0]
            sideMaxRange = block.sizeY
            sideMinRange = 0.0
            currentSideValue = block.sizeX
            sideIndicator = lambda eqRegion: eqRegion.xto
            stepFrom = lambda eqRegion: eqRegion.yfrom
            stepTo = lambda eqRegion: eqRegion.yto
        bCondList = list()    
        var_min = sideMinRange
# Идем по стороне. Определяем все области, в которых заданы и дефолтные и недефолтные уравнения.
        while var_min < sideMaxRange:
            varMaxLst = []
            for eqRegion in block.equationRegions:
                if sideIndicator(eqRegion) == currentSideValue and stepFrom(eqRegion) >= var_min:
                    varMaxLst.append(eqRegion)
            if len(varMaxLst) == 0:
                equationNumber = block.defaultEquation
                equation = self.equations[equationNumber]
                if side == 2 or side == 3 :
                    ranges = [[var_min, sideMaxRange], [currentSideValue, currentSideValue]]
                else:
                    ranges = [[currentSideValue, currentSideValue], [var_min, sideMaxRange]]
                var_min = sideMaxRange
            else:
                varMaxReg = min(varMaxLst, key = stepFrom)
                var_max = stepFrom(varMaxReg)
                if var_max > var_min:
                    equationNumber = block.defaultEquation
                    equation = self.equations[equationNumber]
                    if side == 2 or side == 3 :
                        ranges = [[var_min, var_max], [currentSideValue, currentSideValue]]
                    else:
                        ranges = [[currentSideValue, currentSideValue], [var_min, var_max]]
                    var_min = var_max
                elif var_max == var_min:
                    equationNumber = varMaxReg.equationNumber
                    equation = self.equations[equationNumber]
                    if side == 2 or side == 3:
                        ranges = [[var_min, stepTo(varMaxReg)], [currentSideValue, currentSideValue]]
                    else:
                        ranges = [[currentSideValue, currentSideValue], [var_min, stepTo(varMaxReg)]]
                    var_min = stepTo(varMaxReg) + cellLen * (stepFrom(varMaxReg) == stepTo(varMaxReg))
# Для каждой из таких областей определяем все области, где заданы дефолтные и недефолтные граничные условия.
            bCondList.extend(self.createListOfBCondsForPartOfSide(block, blockNumber, side, ranges, equationNumber, equation, stepFrom, stepTo, cellLen))
# Если отдельное уравнение задано на прямой y = y_max или x = x_max
        if var_min == sideMaxRange:
            for eqRegion in block.equationRegions:
                if sideIndicator(eqRegion) == currentSideValue and stepFrom(eqRegion) == var_min:
                    equationNumber = eqRegion.equationNumber
                    equation = self.equations[equationNumber]
                    if side == 2 or side == 3 :
                        ranges = [[var_min, sideMaxRange], [currentSideValue, currentSideValue]]
                    else:
                        ranges = [[currentSideValue, currentSideValue], [var_min, sideMaxRange]]
                    bCondList.extend(self.createListOfBCondsForPartOfSide(block, blockNumber, side, ranges, equationNumber, equation, stepFrom, stepTo, cellLen))
        return bCondList
    
    def createListOfBCondsForPartOfSide(self, block, blockNumber, side, ranges, equationNum, equation, stepFrom, stepTo, cellLen):
        if side == 2 or side == 3:
            varRanges = ranges[0]
            secRanges = ranges[1]
        else:
            varRanges = ranges[1]
            secRanges = ranges[0]
        var_min = min(varRanges)
        condList = list()
# Отдельно обрабатывается случай, когда какое-то уравнение задано только на прямой
        if var_min == max(varRanges):
            #Сначала проверяем наличие соединений на этом участке, потом уже -- граничных условий
            for icRegion in block.interconnectRegions:
                if icRegion.side == side and stepFrom(icRegion) <= var_min and stepTo(icRegion) >= var_min:
                    startCellIndex, endCellIndex = determineCellIndexOfStartOfConnection2D(icRegion)
                    secondIndex = icRegion.secondIndex + ' - ' + str(startCellIndex)
                    funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(icRegion.side) + "_Eqn" + str(equationNum) + "_SBlock" + str(icRegion.secondaryBlockNumber)
                    conRanges = [[icRegion.xfrom, icRegion.xto], [icRegion.yfrom, icRegion.yto]]
                    condList.append(Connection(icRegion.firstIndex, secondIndex, side, conRanges, equationNum, equation, funcName))
                    break
            else:
                for bRegion in block.boundRegions:
                    if bRegion.side == side and stepFrom(bRegion) <= var_min and stepTo(bRegion) >= var_min:
                        values, btype, boundNumber, funcName = self.setDirichletOrNeumann(bRegion, blockNumber, side, equationNum)
                        break
                else:
                    values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
                bCondRanges = ranges
                condList.append(BoundCondition(values, btype, side, bCondRanges, boundNumber, equationNum, equation, funcName))
            return condList
# Здесь случай, когда уравнение задано в подблоке
        while var_min < max(varRanges):
            varMaxLst = []
            for icRegion in block.interconnectRegions:
                conds = self.SomeConditions(icRegion, stepFrom, stepTo, var_min, max(varRanges))
                if icRegion.side == side and (conds[0] or conds[1] or conds[2]):
                    varMaxLst.append(icRegion)
            for bRegion in block.boundRegions:
                conds = self.SomeConditions(bRegion, stepFrom, stepTo, var_min, max(varRanges))
                if bRegion.side == side and (conds[0] or conds[1] or conds[2]):
                    varMaxLst.append(bRegion)
            if len(varMaxLst) == 0:
                values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
                if side == 2 or side == 3:
                    bCondRanges = [[var_min, max(varRanges)], secRanges]
                else:
                    bCondRanges = [secRanges, [var_min, max(varRanges)]]
                var_min = max(varRanges)
                condList.append(BoundCondition(values, btype, side, bCondRanges, boundNumber, equationNum, equation, funcName))
            else:
                varMaxReg = min(varMaxLst, key = lambda reg: stepFrom(reg))
                conds = self.SomeConditions(varMaxReg, stepFrom, stepTo, var_min, max(varRanges))
                var_max = conds[0] * stepFrom(varMaxReg) + conds[1] * stepTo(varMaxReg) + conds[2] * max(varRanges)
                if var_max > var_min and conds[0]:
                    values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
                    if side == 2 or side == 3:
                        bCondRanges = [[var_min, var_max], secRanges]
                    else:
                        bCondRanges = [secRanges, [var_min, var_max]]
                    var_min = var_max
                    condList.append(BoundCondition(values, btype, side, bCondRanges, boundNumber, equationNum, equation, funcName))
                elif var_max == var_min or var_max > var_min and conds[1] or conds[2]:
                    if side == 2 or side == 3:
                        bCondRanges = [[var_min, min([stepTo(varMaxReg), max(varRanges)])], secRanges]
                    else:
                        bCondRanges = [secRanges, [var_min, min([stepTo(varMaxReg), max(varRanges)])]]
                    var_min = min([stepTo(varMaxReg), max(varRanges)]) + cellLen * (stepFrom(varMaxReg) == stepTo(varMaxReg))
                    #Если там стоит граничное условие
                    if not isinstance(varMaxReg, InterconnectRegion):
                        values, btype, boundNumber, funcName = self.setDirichletOrNeumann(varMaxReg, blockNumber, side, equationNum)
                        condList.append(BoundCondition(values, btype, side, bCondRanges, boundNumber, equationNum, equation, funcName))
                    #Если там стоит соединение
                    else:
                        startCellIndex, endCellIndex = determineCellIndexOfStartOfConnection2D(varMaxReg)
                        secondIndex = varMaxReg.secondIndex + ' - ' + str(startCellIndex)
                        funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(varMaxReg.side) + "_Eqn" + str(equationNum) + "_SBlock" + str(varMaxReg.secondaryBlockNumber)
                        condList.append(Connection(varMaxReg.firstIndex, secondIndex, side, bCondRanges, equationNum, equation, funcName))
        return condList
  
    def generateBoundsAndIcs(self, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst):
        #  ***x->
        #  *  
        #  |  ---side 2---
        #  y  |          |
        #     s          s
        #     i          i
        #     d          d
        #     e          e
        #     0          1
        #     |          |
        #     ---side 3---  
        parser = MathExpressionParser()
        parsedAngleCondList = self.createACL(totalBCondLst, parser)
        intro = '\n//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'
        outputStr = [intro]
        outputStr.append(self.generateVertexFunctions(blockNumber, arrWithFunctionNames, parsedAngleCondList))      
        
        #counter for elements in blockFunctionMap including subdictionaries
        bfmLen = len(arrWithFunctionNames)
        #dictionary to return to binarymodel
        blockFunctionMap.update({"e02":bfmLen - 4, "e12":bfmLen - 3, "e03":bfmLen - 2, "e13":bfmLen - 1 })
        for num, bCondLst in enumerate(totalBCondLst):
            side = 2 * (num == 0) + 3 * (num == 1) + 1 * (num == 3)
            boundaryName = determineNameOfBoundary(side)
            #subdictionary for every side 
            sideLst = []
            sideName = "side"+str(side)          
            #Этот список нужен для исключения повторяющихся функций
            boundAndEquatNumbersList = list()
            for condition in bCondLst:
                #Если для граничного условия с таким номером функцию уже создали, то заново создавать не надо.
                if self.EquationLieOnSomeBound(condition):
                    continue
                if not isinstance(condition, Connection):
                    if (condition.boundNumber, condition.equationNumber) in boundAndEquatNumbersList:
                        ranges = [condition.ranges[0][0], condition.ranges[0][1], condition.ranges[1][0], condition.ranges[1][1]]
                        sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
                        continue
                    boundAndEquatNumbersList.append((condition.boundNumber, condition.equationNumber))
                    outputStr.append('//Boundary condition for boundary ' + boundaryName + '\n')
                    #Если надо сгенерить граничное условие
                    if condition.btype == 0:
                        outputStr.append(self.generateDirichlet(blockNumber, condition.funcName, condition))
                    else:
                        pBCL = [condition]
                        outputStr.append(self.generateNeumannOrInterconnect(blockNumber, condition.funcName, condition.parsedEquation, condition.unknownVars, pBCL))
                #Если надо сгенерить соединение блоков
                else:
                    outputStr.append('//Interconnect for boundary ' + boundaryName + '\n')
                    pBCL = [condition]
                    outputStr.append(self.generateNeumannOrInterconnect(blockNumber, condition.funcName, condition.parsedEquation, condition.unknownVars, pBCL))
                arrWithFunctionNames.append(condition.funcName)
                ranges = [condition.ranges[0][0], condition.ranges[0][1], condition.ranges[1][0], condition.ranges[1][1]]
                sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
            blockFunctionMap.update({sideName:sideLst}) 
        return ''.join(outputStr)
    
    def EquationLieOnSomeBound(self, condition):
        return condition.ranges[0][0] == condition.ranges[0][1] and condition.ranges[1][0] == condition.ranges[1][1]
    
    def SomeConditions(self, bRegion, stepFrom, stepTo, vmin, vmax):
        cond1 = stepFrom(bRegion) >= vmin and stepFrom(bRegion) <= vmax
        cond2 = stepTo(bRegion) > vmin and stepTo(bRegion) <= vmax and stepFrom(bRegion) < vmin
        cond3 = stepFrom(bRegion) < vmin and stepTo(bRegion) > vmax
        return [cond1, cond2, cond3]
    
    def generateVertexFunctions(self, blockNumber, arrWithFunctionNames, parsedAngleCondList):
# parsedAngleCondList --- это список пар [[условие 1, условие 2], [условие 1, условие 2], ...]
        output = list()
        icsvCounter = 0
        for angleCond in parsedAngleCondList:
            parsedEqs = angleCond[0].parsedEquation
            unknownVars = angleCond[0].unknownVars
            
            boundaryName1 = determineNameOfBoundary(angleCond[0].side)
            boundaryName2 = determineNameOfBoundary(angleCond[1].side)
            funcIndex = str(angleCond[0].side) + '_' + str(angleCond[1].side) + '__Eqn' + str(angleCond[0].equationNumber)
            if not isinstance(angleCond[0], Connection) and not isinstance(angleCond[1], Connection):
                if angleCond[0].boundNumber == angleCond[1].boundNumber == -1:
                    output.append('//Default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if angleCond[0].btype == angleCond[1].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'Neumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                elif angleCond[0].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[0])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[1])])
            elif isinstance(angleCond[0], Connection) and not isinstance(angleCond[1], Connection):
                if angleCond[1].boundNumber == -1:
                    output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if angleCond[1].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[1])])
            elif not isinstance(angleCond[0], Connection) and isinstance(angleCond[1], Connection):
                if angleCond[0].boundNumber == -1:
                    output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if angleCond[0].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[0])])
            else:
                output.append('//Interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                nameForVertex = 'Block' + str(blockNumber) + 'Interconnect__Vertex' + funcIndex
                output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
                icsvCounter += 1
            
            arrWithFunctionNames.append(nameForVertex)
        return ''.join(output)
        
class generator3D(abstractGenerator):
    def __init__(self, equations, blocks, initials, bounds, gridStep):
        super(generator3D,self).__init__(equations, blocks, initials, bounds, gridStep)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(self.system))
            self.allBlockOffsetList.append([block.offsetX, block.offsetY, block.offsetZ])
            self.allBlockSizeList.append([block.sizeX, block.sizeY, block.sizeZ])
            
    def createListWithFuncNamesForBlock(self, blockNumber):
        raise AttributeError("3D case is difficult!")
    
    def generateInitials(self):
#         initials --- массив [{"Name": '', "Values": []}, {"Name": '', "Values": []}]
        output = list(["//===================PARAMETERS==========================//\n\n"])
        output.append(self.generateParamFunction())
        output.append("//===================INITIAL CONDITIONS==========================//\n\n")

        pointInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames = self.generateAllPointInitials()
        output.append(pointInitials)
        output.append(self.generateFillInitValFuncsForAllBlocks(listWithInitialFunctionNames, listWithDirichletFunctionNames))
        output.append(self.generateGetInitFuncArray())
        
        return ''.join(output) 
    
    def generateFillInitValFuncsForAllBlocks(self, listWithInitialFunctionNames, listWithDirichletFunctionNames):
#         Для каждого блока создает функцию-заполнитель с именем BlockIFillInitialValues (I-номер блока)
        totalCountOfInitials = len(listWithInitialFunctionNames)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
            strBlockNum = str(blockNumber)
            fillFunction = self.genCommonPartForFillInitValFunc(block, blockNumber, totalCountOfInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames)
            fillFunction += "\tfor(int idxZ = 0; idxZ<Block" + strBlockNum + "CountZ; idxZ++)\n"
            fillFunction += "\t\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n"
            fillFunction += "\t\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n"
            fillFunction += "\t\t\t\tint idx = idxZ*Block" + strBlockNum + "CountY*Block" + strBlockNum + "CountX + idxY*Block" + strBlockNum + "CountX + idxX;\n"
            fillFunction += "\t\t\t\tint type = initType[idx];\n"
            fillFunction += "\t\t\t\tinitFuncArray[type](result+idx*Block" + strBlockNum + "CELLSIZE, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, Block" + strBlockNum + "OffsetZ + idxZ*DZ);\n\t\t\t}\n"
            fillFunction += "}\n\n"
            allFillFunctions.append(fillFunction)
        return ''.join(allFillFunctions)
    
    def getBlockInfo(self, block, blockNumber):
# Возвращает границы блока и особый список всех граничных условий
# Offset -- это смещение блока, Size -- длина границы, поэтому границы блока -- это [Offset, Offset + Size]
        minRanges = [block.offsetX, block.offsetY, block.offsetZ]
        maxRanges = [block.offsetX + block.sizeX, block.offsetY + block.sizeY, block.offsetZ + block.sizeZ]
        blockRanges = dict({'min' : minRanges, 'max' : maxRanges})
# boundaryConditionList -- это [{'values':[], 'type':тип, 'side':номер границы, 'boundNumber': номер условия, 'ranges':[[xFrom,xTo],[y],[z]]}]
        boundaryConditionList = list()
        for region in block.boundRegions:
            if region.boundNumber >= len(self.bounds):
                raise AttributeError("Non-existent number of boundary condition is set for some boundary region in array 'Blocks'!")
            if region.side == 0:
                boundaryRanges = [[block.offsetX, block.offsetX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
            elif region.side == 1:
                boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
            elif region.side == 2:
                boundaryRanges = [[region.xfrom, region.xto], [block.offsetY, block.offsetY], [region.zfrom, region.zto]]
            elif region.side == 3:
                boundaryRanges = [[region.xfrom, region.xto], [block.offsetY + block.sizeY, block.offsetY + block.sizeY], [region.zfrom, region.zto]]
            elif region.side == 4:
                boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ, block.offsetZ]]
            elif region.side == 5:
                boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ + block.sizeZ, block.offsetZ + block.sizeZ]]

            bound = self.bounds[region.boundNumber]
            #Если условие Дирихле, то используем производные по t,
            #если Неймановское условие --- то сами значения.
            if bound.btype == 0:
                values = list(bound.derivative)
            elif bound.btype == 1:
                values = list(bound.values)
#                 Исправление понятия Неймановского условия
                if region.side == 0 or region.side == 2 or region.side == 4:
                    for idx, value in enumerate(values):
                        values.pop(idx)
                        values.insert(idx, '-(' + value + ')')
            NeumannValues = list(values) 
            bCond = BoundCondition(NeumannValues, bound.btype, region.side, boundaryRanges, region.boundNumber)
            boundaryConditionList.append(bCond)
        return blockRanges, boundaryConditionList
    
    def generateDefaultBoundaryFunction(self, blockNumber, parsedEquationsList):
        defaultFunctions = list()
        parser = MathExpressionParser()
        variables = parser.getVariableList(self.system)
             
        defuaultBoundaryConditionValues = len(variables) * ['0.0']
        
        intro = '\n//=========================DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'       
        defaultFunctions.append(intro)
                 
        for i in range(0, 6):
            boundaryName = determineNameOfBoundary(i)
            defaultFunctions.append('//Default boundary condition for boundary ' + boundaryName + '\n')
            nameForSide = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(i)
            defaultBoundaryConditionList = list([tuple((i, defuaultBoundaryConditionValues))])
            defaultFunctions.append(self.generateNeumannOrInterconnect(blockNumber, nameForSide, parsedEquationsList, variables, defaultBoundaryConditionList))
            
        ribs = [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)]
        for rib in ribs:
            boundaryName1 = determineNameOfBoundary(rib[0])
            boundaryName2 = determineNameOfBoundary(rib[1])
            defaultFunctions.extend(['//Default boundary condition for rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
            defaultBoundaryConditionList = list([tuple((rib[0], defuaultBoundaryConditionValues)), tuple((rib[1], defuaultBoundaryConditionValues))])
            nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1])
            defaultFunctions.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEquationsList, variables, defaultBoundaryConditionList)])     
        return ''.join(defaultFunctions)
    
    def generateBoundsAndIcs(self, blockNumber, arrWithFunctionNames, blockRanges, boundaryConditionList):
        parser = MathExpressionParser()
        variables = parser.getVariableList(self.system)
        parsedBoundaryConditionDictionary, parsedEquationsList = self.createPBCDandPEL(boundaryConditionList, parser, variables)
        
        outputStr = list(self.generateDefaultBoundaryFunction(blockNumber, parsedEquationsList))
        intro = '\n//=============================OTHER BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'
        outputStr.append(intro)
        
        properSequenceOfSides = [2,3,0,1]
        #  ***x->
        #  *  
        #  |  ---side 2---
        #  y  |          |
        #     s          s
        #     i          i
        #     d          d
        #     e          e
        #     0          1
        #     |          |
        #     ---side 3---        
        
        #dictionary to return to binarymodel
        blockFunctionMap = {"center":0, "e02":1, "e12":2, "e03":3, "e13":4 } 
        #counter for elements in blockFunctionMap including subdictionaries
        bfmLen = 5
        #for side in range(0, boundaryCount):
        for side in properSequenceOfSides:
            #subdictionary for every side 
            sideMap = {}
            sideName = "side"+str(side)
                        
            boundaryName = determineNameOfBoundary(side)
            defaultFuncName = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(side)
            arrWithFunctionNames.append(defaultFuncName)
            #every time we append a name to arrWithFunctionNames we should also  
            sideMap = {"default":bfmLen}
            bfmLen += 1
            #Генерируем функции для всех заданных условий и кладем их имена в массив
            if side not in parsedBoundaryConditionDictionary:
                blockFunctionMap.update({sideName:sideMap})
                continue
            counter = 0
            #Это список номеров граничных условий для данной стороны side. Нужен для исключения повторяющихся функций,
            #т.к. на одну сторону в разных местах м.б. наложено одно и то же условие
            boundNumberList = list()
            for condition in parsedBoundaryConditionDictionary[side]:
                #Если для граничного условия с таким номером функцию еще не создавали, то создать, иначе - не надо.
                if condition.boundNumber in boundNumberList:
                    continue
                boundNumberList.append(condition.boundNumber)
                parsedBoundaryConditionTuple = list([tuple((side, condition.parsedValues))])
                raise AttributeError("Three-dimensional case is difficult!")
                counter += 1
            blockFunctionMap.update({sideName:sideMap}) 
        outputStr.extend(self.generateVertexAndRibFunctions(blockNumber, arrWithFunctionNames, blockRanges, parsedEquationsList, variables, parsedBoundaryConditionDictionary))
        return ''.join(outputStr), blockFunctionMap
    
    def generateVertexAndRibFunctions(self, blockNumber, arrWithFunctionNames, blockRanges, parsedEstrList, variables, parsedBoundaryConditionDictionary):
#         blockRanges --- это словарь {'min' : [x_min,y_min,z_min], 'max' : [x_max,y_max,z_max]}
#         parsedBoundaryConditionDictionary {Номер границы : [(распарсенное условие 1, [4 или 2 координаты краев части 1 границы], Тип условия),
#                                                             (распарсенное условие 2, [4 или 2 координаты краев части 2 границы], Тип условия), ...]}
#         [координаты краев части 1 границы] содержат 4 точки
        output = list([])
        defuaultBoundaryConditionValues = len(variables) * ['0.0']

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
            boundaryName1 = determineNameOfBoundary(rib[0])
            boundaryName2 = determineNameOfBoundary(rib[1])
            pairsOfBoundaryCondition = list()
            if rib[0] in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                boundary1CondList = parsedBoundaryConditionDictionary[rib[0]]
                boundary2CondList = parsedBoundaryConditionDictionary[rib[1]]
                pairsOfBoundaryCondition = self.algorithmForRib(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundary1CondList, boundary2CondList, defuaultBoundaryConditionValues)
            elif rib[0] in parsedBoundaryConditionDictionary and rib[1] not in parsedBoundaryConditionDictionary:
#                     Здесь надо сначала определить те границы, которые касаются ребра, и для каждой из них
#                     сгенерить функцию
                for boundaryCondition in parsedBoundaryConditionDictionary[rib[0]]:
                    if len(self.rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                        pairsOfBoundaryCondition.append(((boundaryCondition[0],boundaryCondition[2]), (defuaultBoundaryConditionValues,1)))
            elif rib[0] not in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                for boundaryCondition in parsedBoundaryConditionDictionary[rib[1]]:
                    if len(self.rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                        pairsOfBoundaryCondition.append(((defuaultBoundaryConditionValues,1), (boundaryCondition[0],boundaryCondition[2])))
            else:
                continue
            for number,pair in enumerate(pairsOfBoundaryCondition):
                output.extend(['//Non-default boundary condition for RIB between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + ' with number ' + str(number) + '\n'])
                if pair[0][1] == pair[1][1] == 1:
                    nameForRib = 'Block' + str(blockNumber) + 'NeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                    boundaryConditionList = list([tuple((rib[0], pair[0][0])), tuple((rib[1], pair[1][0]))])
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForRib, parsedEstrList, variables, boundaryConditionList)])
                elif pair[0][1] == 0:
                    nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                    boundaryConditionList = list([tuple((rib[0], pair[0][0]))])
                    output.extend([self.generateDirichlet(blockNumber, nameForRib, boundaryConditionList)])
                else:
                    nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                    boundaryConditionList = list([tuple((rib[1], pair[1][0]))])
                    output.extend([self.generateDirichlet(blockNumber, nameForRib, boundaryConditionList)])
        
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
            
            boundaryName1 = determineNameOfBoundary(Vertex[0])
            boundaryName2 = determineNameOfBoundary(Vertex[1])
            boundaryName3 = determineNameOfBoundary(Vertex[2])
            output.extend(['//Non-default boundary condition for Vertex between boundaries ' + boundaryName1 + ', ' + boundaryName2 + ' and ' + boundaryName3 + '\n'])
            if type1 == type2 == type3 == 1:
                boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue)), tuple((Vertex[2], bound3CondValue))])
                nameForVertex = 'Block' + str(blockNumber) + 'NeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEstrList, variables, boundaryConditionList)])
            elif type1 == 0:
                boundaryConditionList = list([tuple((Vertex[0], bound1CondValue))])
                nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                output.extend([self.generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
            elif type2 == 0:
                boundaryConditionList = list([tuple((Vertex[1], bound2CondValue))])
                nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                output.extend([self.generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
            else:
                boundaryConditionList = list([tuple((Vertex[2], bound3CondValue))])
                nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                output.extend([self.generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])

        return output
    
    def rectVertexNearSegment(self, ribCoordinateMin, ribCoordinateMax, rectCoordinateList):
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
        goodPoints = list()
        differentCoord = list()
        for (reducedCoord, originalCoord) in zip(reducedRectCoordList, rectCoordinateList):
            left = (reducedCoord[0] - reducedRibCoordinateMax[0]) * (reducedRibCoordinateMin[1] - reducedRibCoordinateMax[1])
            right = (reducedCoord[1] - reducedRibCoordinateMax[1]) * (reducedRibCoordinateMin[0] - reducedRibCoordinateMax[0])
            if left == right and reducedCoord[index] <= reducedRibCoordinateMax[index] and reducedCoord[index] >= reducedRibCoordinateMin[index]:
                goodPoints.extend([originalCoord])
                differentCoord.extend([reducedCoord[index]])
        
        return tuple((goodPoints, differentCoord))
    
    def computeSideLength2D(self, blockRanges, Side):
#         blockRanges --- словарь {"min": [x,y,z], "max": [x,y,z]}
#         side --- номер стороны, длину которой надо вычислить       
        if Side == 0 or Side == 1:
            return blockRanges["max"][1] - blockRanges["min"][1]
        elif Side == 2 or Side == 3:
            return blockRanges["max"][0] - blockRanges["min"][0]
        else:
            raise AttributeError("Side should be 0, 1, 2 or 3!")
     
    def computeSegmentLength2D(self, segment):
#         segment = [(x1,y1),(x2,y2)]
        if len(segment) != 2 or len(segment[0]) != 2 or len(segment[1]) != 2:
            raise AttributeError("List 'segment' in computeSegmentLength2D() should contain exactly two elements!")
#         т.к. отрезки параллельны осям кординат, то можно делать так
        reducedSegment = []
#         Двумерный случай сводится к одномерному
        if segment[0][0] == segment[1][0]:
            reducedSegment = [min([segment[0][1], segment[1][1]]), max([segment[0][1], segment[1][1]])]
        elif segment[0][1] == segment[1][1]:
            reducedSegment = [min([segment[0][0], segment[1][0]]), max([segment[0][0], segment[1][0]])]
             
        return reducedSegment[1] - reducedSegment[0]
        
    def segmentsIntersects(self, segment1, segment2):
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
     
    def determineAllPairsOfConditions(self, resultCondList1, resultCondList2, defaultBoundaryConditions):
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
                    if self.segmentsIntersects(boundaryCond1[3], boundaryCond2[3]):
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
     
    def algorithmForRib(self, ribCoordinateMin, ribCoordinateMax, boundary1CondList, boundary2CondList, defaultBoundaryConditions):
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
                pointsOnRib = self.rectVertexNearSegment(ribCoordinateMin, ribCoordinateMax, boundaryCondition[1])
                if len(pointsOnRib[0]) == 2:
#                     (Сами условия, координаты углов, список координат углов на ребре, координаты одномерного отрезка, Тип условия)
                    resultCondList.extend([(boundaryCondition[0], boundaryCondition[1], pointsOnRib[0], pointsOnRib[1], boundaryCondition[2])])
         
#         Шаг 2: теперь составляем всевозможные пары условий (Условие на 1 границу, условие на 2 границу):
#         для каждого условия первой границы берем все подходящие условия второй, и наоборот.
#         Потом их объединяем и возвращаем в виде списка.
        finalResultCondList1 = self.determineAllPairsOfConditions(generalResultCondList[0], generalResultCondList[1], defaultBoundaryConditions)
        finalResultCondList2 = self.determineAllPairsOfConditions(generalResultCondList[1], generalResultCondList[0], defaultBoundaryConditions)
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
    