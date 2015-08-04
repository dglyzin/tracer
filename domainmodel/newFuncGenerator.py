# -*- coding: utf-8 -*-
from equationParser import MathExpressionParser
from someFuncs import generateCodeForMathFunction, determineNameOfBoundary, squareOrVolume, determineCellIndexOfStartOfConnection2D, getRanges, splitBigRect, intersectionOfRects
from rhsCodeGenerator import RHSCodeGenerator

class FuncGenerator:
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex, preprocessorFolder):
        dimension = len(equations[0].vars)
        if dimension == 1:
            self.generator = generator1D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        elif dimension == 2:
            self.generator = generator2D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        else:
            self.generator = generator3D(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.preprocessorFolder = preprocessorFolder
    
    def generateAllFunctions(self):
        #gridStep --- список [gridStepX, gridStepY, gridStepZ]
        outputStr = '#include <math.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include "' +self.preprocessorFolder +  '/doc/userfuncs.h"\n\n'
        outputStr += self.generator.generateAllDefinitions()
        outputStr += self.generator.generateInitials()
        
        totalArrWithFunctionNames = list()
        functionMaps = []
        for blockNumber, block in enumerate(self.generator.blocks):
            systemsForCentralFuncs, numsForSystems, totalBCondLst, totalInterconnectLst, blockFunctionMap = self.generator.getBlockInfo(block, blockNumber)
            cf, arrWithFunctionNames = self.generator.generateCentralFunctionCode(block, blockNumber, systemsForCentralFuncs, numsForSystems)
            bf = self.generator.generateBoundsAndIcs(block, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst)
            
            totalArrWithFunctionNames.append(arrWithFunctionNames)
            functionMaps.append(blockFunctionMap)
            print blockFunctionMap
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
        self.parsedValues = list()
        for value in self.values:
            self.parsedValues.append(mathParser.parseMathExpression(value, params, indepVars))
        
        self.unknownVars = mathParser.getVariableList(self.equation.system)    
        self.parsedEquation = list()
        for equat in self.equation.system:
            self.parsedEquation.extend([mathParser.parseMathExpression(equat, self.unknownVars, params, self.equation.vars)])
            
    def setRibsAndVertexesIn3D(self, ribs, vertexes):
        self.ribs = ribs
        self.vertexes = vertexes

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
        #Парсит краевые условия и создает список условий на углы (angleCondList) 
        for bCondListForSide in totalBCondLst:  
            for bCond in bCondListForSide:
                indepVarsForBoundaryFunction = list(self.userIndepVars)
                indepVarsForBoundaryFunction.remove(self.userIndepVars[bCond.side // 2])
                indepVarsForBoundaryFunction.extend(['t'])
                
                if not isinstance(bCond, Connection):
                    bCond.createSpecialProperties(parser, self.params, indepVarsForBoundaryFunction)
                else:
                    bCond.createSpecialProperties(parser, self.params)
        #Создание списка условий на углы. В него входят условия с уже распарсенными значениями        
        condCntOnS2 = len(totalBCondLst[0])
        condCntOnS3 = len(totalBCondLst[1])
        condCntOnS0 = len(totalBCondLst[2])
        condCntOnS1 = len(totalBCondLst[3])
        angleCondList = [[totalBCondLst[0][0], totalBCondLst[2][0]], [totalBCondLst[0][condCntOnS2-1], totalBCondLst[3][0]],
                         [totalBCondLst[1][0], totalBCondLst[2][condCntOnS0-1]], [totalBCondLst[1][condCntOnS3-1], totalBCondLst[3][condCntOnS1-1]]]
        return angleCondList
    
    def setDefault(self, blockNumber, side, equation, equationNum):
        systemLen = len(equation.system)
        funcName = "Block" + str(blockNumber) + "DefaultNeumann__Bound" + str(side) + "__Eqn" + str(equationNum)
        return systemLen * ['0.0'], 1, -1, funcName
    
    def setDirichletOrNeumann(self, bRegion, blockNumber, side, equationNum):
        boundNumber = bRegion.boundNumber
        btype = self.bounds[boundNumber].btype
        if btype == 0:
            funcName = "Block" + str(blockNumber) + "Dirichlet__Bound" + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum)
            outputValues = list(self.bounds[boundNumber].derivative)
        elif btype == 1:
            funcName = "Block" + str(blockNumber) + "Neumann__Bound" + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum)
            outputValues = list(self.bounds[boundNumber].values)
            #Особенность Неймановского условия
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
            indepVarValueList.extend(['(idx' + indepVar.upper() + ' + Block' + str(blockNumber) + 'Offset' + indepVar.upper() + ' * D' + indepVar.upper() + 'M1' + ')'])
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
                #Каждую функцию характеризует не длина в координатах, а диапазон клеток, которые эта функция должна пересчитывать
                ranges = getRanges([eqRegion.xfrom, eqRegion.xto, self.gridStep[0], block.sizeX])
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber)] + ranges)
                #blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber), eqRegion.xfrom, eqRegion.xto])
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
                
    def generateBoundsAndIcs(self, block, blockNumber, arrWithFunctionNames, blockFunctionMap, bCondLst, icsList):
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
            reservedSquare += squareOrVolume([eqRegion.xfrom, eqRegion.xto], [eqRegion.yfrom, eqRegion.yto])
            if eqRegion.equationNumber not in numsForSystems and not cond1 and not cond2:
                systemsForCentralFuncs.append(self.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)
            if not cond1 and not cond2:
                ranges = getRanges([eqRegion.xfrom, eqRegion.xto, self.gridStep[0], block.sizeX], [eqRegion.yfrom, eqRegion.yto, self.gridStep[1], block.sizeY])
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber)] + ranges)
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
        #Отдельно обрабатывается случай, когда какое-то уравнение задано только на прямой
        if var_min == max(varRanges):
            #Сначала проверяем наличие соединений на этом участке, потом уже -- граничных условий
            for icRegion in block.interconnectRegions:
                if icRegion.side == side and stepFrom(icRegion) <= var_min and stepTo(icRegion) >= var_min:
                    startCellIndex, endCellIndex = determineCellIndexOfStartOfConnection2D(icRegion)
                    secondIndex = '(' + icRegion.secondIndex + ' - ' + str(startCellIndex) + ') * Block' + str(blockNumber) + 'CELLSIZE'
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
        #Здесь случай, когда уравнение задано в подблоке
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
                        secondIndex = '(' + varMaxReg.secondIndex + ' - ' + str(startCellIndex) + ') * Block' + str(blockNumber) + 'CELLSIZE'
                        funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(varMaxReg.side) + "_Eqn" + str(equationNum) + "_SBlock" + str(varMaxReg.secondaryBlockNumber)
                        condList.append(Connection(varMaxReg.firstIndex, secondIndex, side, bCondRanges, equationNum, equation, funcName))
        return condList
  
    def generateBoundsAndIcs(self, block, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst):
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
                        ranges = getRanges([condition.ranges[0][0], condition.ranges[0][1], self.gridStep[0], block.sizeX], [condition.ranges[1][0], condition.ranges[1][1], self.gridStep[1], block.sizeY])
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
                ranges = getRanges([condition.ranges[0][0], condition.ranges[0][1], self.gridStep[0], block.sizeX], [condition.ranges[1][0], condition.ranges[1][1], self.gridStep[1], block.sizeY])
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
    def __init__(self, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(generator3D,self).__init__(equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(equations[block.defaultEquation].system))
            self.allBlockOffsetList.append([block.offsetX, block.offsetY, block.offsetZ])
            self.allBlockSizeList.append([block.sizeX, block.sizeY, block.sizeZ])
#             self.__createBlockIcsRegions(block)
            
    def generateFillInitValFuncsForAllBlocks(self, listWithInitialFunctionNames, listWithDirichletFunctionNames):
        #Для каждого блока создает функцию-заполнитель с именем BlockIFillInitialValues (I-номер блока)
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
        systemsForCentralFuncs = []
        numsForSystems = []
        blockFuncMap = {'center': []}
        blockVolume = block.sizeX * block.sizeY * block.sizeZ
        reservedVolume = 0
        for eqRegion in block.equationRegions:
            cond1 = eqRegion.xfrom == eqRegion.xto and (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX)
            cond2 = eqRegion.yfrom == eqRegion.yto and (eqRegion.yto == 0.0 or eqRegion.yto == block.sizeY)
            cond3 = eqRegion.zfrom == eqRegion.zto and (eqRegion.zto == 0.0 or eqRegion.zto == block.sizeZ)
            reservedVolume += squareOrVolume([eqRegion.xfrom, eqRegion.xto], [eqRegion.yfrom, eqRegion.yto], [eqRegion.zfrom, eqRegion.zto])
            if eqRegion.equationNumber not in numsForSystems and not cond1 and not cond2 and not cond3:
                systemsForCentralFuncs.append(self.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)
            if not cond1 and not cond2 and not cond3:
                ranges = getRanges([eqRegion.xfrom, eqRegion.xto, self.gridStep[0], block.sizeX], [eqRegion.yfrom, eqRegion.yto, self.gridStep[1], block.sizeY], [eqRegion.zfrom, eqRegion.zto, self.gridStep[2], block.sizeZ])
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber)] + ranges)
        if blockVolume > reservedVolume:
            systemsForCentralFuncs.append(self.equations[block.defaultEquation])
            blockFuncMap.update({'center_default': len(numsForSystems)})
            numsForSystems.append(block.defaultEquation)
        
        totalBCondLst = list()
        sides = [4,5,2,3,0,1]
        for side in sides:
            totalBCondLst.append(self.createListOfBCondsForSide(block, blockNumber, side))
        
        return systemsForCentralFuncs, numsForSystems, totalBCondLst, [], blockFuncMap

    def createListOfBCondsForSide(self, block, blockNumber, side):
        bCondList = []
        sidec1from, sidec1to, sidec2from, sidec2to = self.sideConfigs2(block, side)
        boundary = [sidec1from, sidec1to, sidec2from, sidec2to]
        ribsNames, vertexesNames = self.sideConfigs3(block, side)
        #В массиве allRectsOnSide будут содержаться словари вида {'ranges', 'eNum', 'e'}, каждый из которых соответствует какому-то
        #прямоугольнику на границе
        allRectsOnSide = self.determineSpaceOnTheBoundWithDefaultEquation(block, side)
        #Идем по всем прямоугольникам на границе и создаем для каждого из них одно или несколько краевых условий
        for rectMap in allRectsOnSide:
            dRect = rectMap['ranges']
            equationNum = rectMap['eNum']
            equation = rectMap['e']
            newDomainAfterSpliting = [dRect]
            for bRegion in block.boundRegions:
                #Находим очередное граничное условие на данную границу; это прямоугольник
                if bRegion.side != side:
                    continue
                if side == 0 or side == 1:
                    rect = [bRegion.yfrom, bRegion.yto, bRegion.zfrom, bRegion.zto]
                elif side == 2 or side == 3:
                    rect = [bRegion.xfrom, bRegion.xto, bRegion.zfrom, bRegion.zto]
                else:
                    rect = [bRegion.xfrom, bRegion.xto, bRegion.yfrom, bRegion.yto]
                    
                domainAfterSpliting = newDomainAfterSpliting
                newDomainAfterSpliting = []
                cntOfIntersections = 0
                for rectWithEq in domainAfterSpliting:
                    #посмотрим, пересекаются ли регионы. Если да, то создадим условие для пересечения. Сделаем сплит и, пока
                    #не закончатся граничные условия либо пока разность не станет пуста, будем искать пересечения и сплитить.
                    #В конце посмотрим, пуста ли разность. Если нет, то создадим дефолтное Неймановское условие
                    intersection = intersectionOfRects(rectWithEq, rect)
                    if len(intersection) == 0:
                        continue
                    cntOfIntersections += 1
                    #Здесь, разумеется, будут повторные названия функций. Это учтется потом
                    values, btype, boundNumber, funcName = self.setDirichletOrNeumann(bRegion, blockNumber, side, equationNum)
                    #Находим все ребра (и их координаты относительно ребра) и углы, которых касается прямоугольник
                    ribs, vertexes = self.createVertexAndRibLsts(intersection, boundary, ribsNames, vertexesNames)
                    #Создаем новое граничное условие
                    ranges = self.determine3DCoordinatesForBCond(block, side, intersection)
                    condition = BoundCondition(values, btype, side, ranges, boundNumber, equationNum, equation, funcName)
                    #У него создаем поля с именами и координатами ребер и углов, которых касается прямоугольник
                    condition.setRibsAndVertexesIn3D(ribs, vertexes)
                    bCondList.append(condition)
                    #Находим кусок области, не затронутый граничным условием
                    rectsAfterSpliting = splitBigRect(rectWithEq, intersection)
                    #Если на всем очередном прямоугольнике задано граничное условие, то переходим к следующему
                    if len(rectsAfterSpliting) == 0:
                        continue
                    newDomainAfterSpliting.extend(rectsAfterSpliting)
                #newDomainAfterSpliting может быть пуст в 2 случаях:
                #1. Если среди первых нескольких граничных регионов нашлись те, которые покрывают весь dRect;
                #2. Если очередное граничное условие не имеет ни одного пересечения с каждой из областей в domainAfterSpliting;
                if len(newDomainAfterSpliting) != 0:
                    continue
                #В случае 1 досрочно прервается цикл по граничным регионам
                if cntOfIntersections > 0:
                    break
                #В случае 2 надо сохранить остаток области dRect
                else:
                    newDomainAfterSpliting = domainAfterSpliting
            #После цикла по всем граничным регионам от прямоугольника dRect должна остаться область,
            #которую не затронули граничные условия. Если эта область не пуста, то генерируем для каждого прямоугольника
            #из этой области дефолтное условие Неймана.
            if len(newDomainAfterSpliting) != 0:
                #defEquationNum = block.defaultEquation
                #defEquation = self.equations[defEquationNum]
                values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
                for domain in newDomainAfterSpliting:
                    ribs, vertexes = self.createVertexAndRibLsts(domain, boundary, ribsNames, vertexesNames)
                    ranges = self.determine3DCoordinatesForBCond(block, side, domain)
                    defCondition = BoundCondition(values, btype, side, ranges, boundNumber, equationNum, equation, funcName)
                    defCondition.setRibsAndVertexesIn3D(ribs, vertexes)
                    bCondList.append(defCondition)
        #На выходе каждый экземпляр граничного условия содержит инфу об углах и ребрах; этим надо пользоваться при генерировании условий на них
        return bCondList
    
    def determineSpaceOnTheBoundWithDefaultEquation(self, block, side):
        #Так как в 3D граница -- это прямоугольник, то функция определяет прямоугольные области
        #внутри этого прямоугольника, на которых задано уравнение по умолчанию;
        #Возвращает список таких областей и список областей на границе с уравнениями не по умолчанию
        sideCharacteristic, regionCharacteristic, c1from, c1to, c2from, c2to = self.sideConfigs1(block, side)
        sidec1from, sidec1to, sidec2from, sidec2to = self.sideConfigs2(block, side)
        #Сначала составим список областей с уравнениями не по умолчанию
        rectsWithNondefaultEquations = []
        for eqRegion in block.equationRegions:
            if regionCharacteristic(eqRegion) == sideCharacteristic:
                #Исключение ситуации, когда проекция региона уравнения на границу является не прямоугольником, а прямой
                if c1from(eqRegion) != c1to(eqRegion) and c2from(eqRegion) != c2to(eqRegion):
                    equationNum = eqRegion.equationNumber
                    equation = self.equations[equationNum]
                    ranges = [c1from(eqRegion), c1to(eqRegion), c2from(eqRegion), c2to(eqRegion)]
                    rectsWithNondefaultEquations.append({'ranges': ranges, 'eNum': equationNum, 'e': equation})
        #Теперь составляем список областей с уравнениями по умолчанию
        rectsWithDefaultEquation = [[sidec1from, sidec1to, sidec2from, sidec2to]]
        iteratedRectsWithDefaultEquation = []
        for smallRect in rectsWithNondefaultEquations:
            for bigRect in rectsWithDefaultEquation:
                #Если smallRect полностью лежит в bigRect, то intersection будет совпадать со smallRect
                sRect = smallRect['ranges']
                intersection = intersectionOfRects(bigRect, sRect)
                if len(intersection) == 0:
                    iteratedRectsWithDefaultEquation.append(bigRect)
                else:
                    newRects = splitBigRect(bigRect, intersection)
                    #Может оказаться так, что весь внешний прямоугольник совпал с внутренним,
                    #значит, на нем задано недефолтное уравнение и его добавлять не надо
                    if len(newRects) != 0:
                        iteratedRectsWithDefaultEquation.extend(newRects)
            rectsWithDefaultEquation = list(iteratedRectsWithDefaultEquation)
        #Здесь rectsWithDefaultEquation это просто список границ регионов, а rectsWithNondefaultEquations это список словарей,
        #где есть поле с границами региона, а также номер уравнения, и само уравнение, список ребер и углов, которых касается прямоугольник
        result = rectsWithNondefaultEquations
        defEquationNum = block.defaultEquation
        defEquation = self.equations[defEquationNum]
        for rect in rectsWithDefaultEquation:
            result.append({'ranges': rect, 'eNum': defEquationNum, 'e': defEquation})
        return result#rectsWithDefaultEquation, rectsWithNondefaultEquations
    
    def sideConfigs1(self, block, side):
        if side / 2 == 0:
            c1from = lambda region: region.yfrom
            c1to = lambda region: region.yto
            c2from = lambda region: region.zfrom
            c2to = lambda region: region.zto
            if side == 0:
                sideCharacteristic = 0
                regionCharacteristic = lambda region: region.xfrom
            else:
                sideCharacteristic = block.sizeX
                regionCharacteristic = lambda region: region.xto
        elif side / 2 == 1:
            c1from = lambda region: region.xfrom
            c1to = lambda region: region.xto
            c2from = lambda region: region.zfrom
            c2to = lambda region: region.zto
            if side == 2:
                sideCharacteristic = 0
                regionCharacteristic = lambda region: region.yfrom
            else:
                sideCharacteristic = block.sizeY
                regionCharacteristic = lambda region: region.yto
        else:
            c1from = lambda region: region.xfrom
            c1to = lambda region: region.xto
            c2from = lambda region: region.yfrom
            c2to = lambda region: region.yto
            if side == 4:
                sideCharacteristic = 0
                regionCharacteristic = lambda region: region.zfrom
            else:
                sideCharacteristic = block.sizeZ
                regionCharacteristic = lambda region: region.zto
        return sideCharacteristic, regionCharacteristic, c1from, c1to, c2from, c2to
    
    def sideConfigs2(self, block, side):
        if side / 2 == 0:
            sidec1from = 0
            sidec1to = block.sizeY
            sidec2from = 0
            sidec2to = block.sizeZ
        elif side / 2 == 1:
            sidec1from = 0
            sidec1to = block.sizeX
            sidec2from = 0
            sidec2to = block.sizeZ
        else:
            sidec1from = 0
            sidec1to = block.sizeX
            sidec2from = 0
            sidec2to = block.sizeY
        return sidec1from, sidec1to, sidec2from, sidec2to
    
    def sideConfigs3(self, block, side):
        if side == 0:
            #Правила именования ребер и углов и размещения их в списке:
            #1. Цифры в названии расположены по возрастанию;
            #2. Порядок их расположения в массиве такой же, как при обходе двумерного блока
            ribsNames = ['02', '03', '04', '05']
            vertexesNames = ['024', '034', '025', '035']
        elif side == 1:
            ribsNames = ['12', '13', '14', '15']
            vertexesNames = ['124', '134', '125', '135']
        elif side == 2:
            ribsNames = ['02', '12', '24', '25']
            vertexesNames = ['024', '124', '025', '125']
        elif side == 3:
            ribsNames = ['03', '13', '34', '35']
            vertexesNames = ['034', '134', '035', '135']
        elif side == 4:
            ribsNames = ['04', '14', '24', '34']
            vertexesNames = ['024', '124', '034', '134']
        else:
            ribsNames = ['05', '15', '25', '35']
            vertexesNames = ['025', '125', '035', '135']
        return ribsNames, vertexesNames
    
    def createVertexAndRibLsts(self, rect, boundary, ribsNames, vertexesNames):
        #Составляет списки ребер и углов, которых касается граничное условие
        #Ребра будут возвращаться в формате списка с элементами вида {"название": [xfrom, xto]} (т.е. координаты относительно ребра!!!)
        ribs = {}
        vertexes = []
        if rect[0] == boundary[0]:
            ribs.update({ribsNames[0]: [rect[2], rect[3]]})
            if rect[2] == boundary[2]:
                vertexes.append(vertexesNames[0])
                ribs.update({ribsNames[2]: [rect[0], rect[1]]})
            if rect[3] == boundary[3]:
                vertexes.append(vertexesNames[2])
                ribs.update({ribsNames[3]: [rect[0], rect[1]]})
        if rect[2] == boundary[2]:
            if ribsNames[2] not in ribs:
                ribs.update({ribsNames[2]: [rect[0], rect[1]]})
            if rect[1] == boundary[1]:
                vertexes.append(vertexesNames[1])
                ribs.update({ribsNames[1]: [rect[2], rect[3]]})
        if rect[1] == boundary[1]:
            if ribsNames[1] not in ribs:
                ribs.update({ribsNames[1]: [rect[2], rect[3]]})
            if rect[3] == boundary[3]:
                vertexes.append(vertexesNames[3])
                if ribsNames[3] not in ribs:
                    ribs.update({ribsNames[3]: [rect[0], rect[1]]})
        if rect[3] == boundary[3]:
            if ribsNames[3] not in ribs:
                ribs.update({ribsNames[3]: [rect[0], rect[1]]})
        return ribs, vertexes

    def determine3DCoordinatesForBCond(self, block, side, coordinates2D):
        if side == 0:
            return [[0, 0], [coordinates2D[0], coordinates2D[1]], [coordinates2D[2], coordinates2D[3]]]
        elif side == 1:
            return [[block.sizeX, block.sizeX], [coordinates2D[0], coordinates2D[1]], [coordinates2D[2], coordinates2D[3]]]
        elif side == 2:
            return [[coordinates2D[0], coordinates2D[1]], [0, 0], [coordinates2D[2], coordinates2D[3]]]
        elif side == 3:
            return [[coordinates2D[0], coordinates2D[1]], [block.sizeY, block.sizeY], [coordinates2D[2], coordinates2D[3]]]
        elif side == 4:
            return [[coordinates2D[0], coordinates2D[1]], [coordinates2D[2], coordinates2D[3]], [0, 0]]
        else:
            return [[coordinates2D[0], coordinates2D[1]], [coordinates2D[2], coordinates2D[3]], [block.sizeZ, block.sizeZ]]
    
    def generateBoundsAndIcs(self, block, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst): 
        parser = MathExpressionParser()
        self.parseBoundaryConditions(totalBCondLst, parser)
        intro = '\n//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'
        outputStr = [intro]
        #Создаем список условий на вершины, затем генерируем функции на вершины. В конце добавляем всю инфу в blockFunctionMap
        parsedVertexCondList = self.createVertexCondLst(totalBCondLst)
        outputStr.append(self.generateVertexFunctions(blockNumber, arrWithFunctionNames, parsedVertexCondList))      
        bfmLen = len(arrWithFunctionNames)
        blockFunctionMap.update({"e024":bfmLen - 8, "e124":bfmLen - 7, "e034":bfmLen - 6, "e134":bfmLen - 5, "e025":bfmLen - 4, "e125":bfmLen - 3, "e035":bfmLen - 2, "e135":bfmLen - 1 })
        #Создаем список условий на ребра, генерируем функции на ребра и добавляем всю инфу в blockFunctionMap
        parsedRibCondList = self.createRibCondLst(totalBCondLst)
        #После работы этой функции словарь parsedRibCondList изменится и будет для каждого ребра содержать
        #список с его условиями. Этот список готов для занесения без изсенений в blockFunctionMap
        outputStr.append(self.generateRibsFunctions(block, blockNumber, arrWithFunctionNames, parsedRibCondList))
        for rib in parsedRibCondList:
            blockFunctionMap.update({"rib" + rib: parsedRibCondList[rib]})
        #Генерируем все краевые условия для обычных границ
        for num, bCondLst in enumerate(totalBCondLst):
            side = 4 * (num == 0) + 5 * (num == 1) + 2 * (num == 2) + 3 * (num == 3) + 1 * (num == 5)
            boundaryName = determineNameOfBoundary(side)
            #subdictionary for every side 
            sideLst = []
            sideName = "side"+str(side)          
            #Этот список нужен для исключения повторяющихся функций
            boundAndEquatNumbersList = []
            for condition in bCondLst:
                if not isinstance(condition, Connection):
                    #Если для граничного условия с таким номером функцию уже создали, то заново создавать не надо.
                    if (condition.boundNumber, condition.equationNumber) in boundAndEquatNumbersList:
                        ranges = getRanges([condition.ranges[0][0], condition.ranges[0][1], self.gridStep[0], block.sizeX], [condition.ranges[1][0], condition.ranges[1][1], self.gridStep[1], block.sizeY], [condition.ranges[2][0], condition.ranges[2][1], self.gridStep[2], block.sizeZ])
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
                ranges = getRanges([condition.ranges[0][0], condition.ranges[0][1], self.gridStep[0], block.sizeX], [condition.ranges[1][0], condition.ranges[1][1], self.gridStep[1], block.sizeY], [condition.ranges[2][0], condition.ranges[2][1], self.gridStep[2], block.sizeZ])
                sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
            blockFunctionMap.update({sideName:sideLst}) 
        return ''.join(outputStr)
    
    def parseBoundaryConditions(self, totalBCondLst, parser):
        #Парсит краевые условия 
        for bCondListForSide in totalBCondLst:  
            for bCond in bCondListForSide:
                indepVarsForBoundaryFunction = list(self.userIndepVars)
                indepVarsForBoundaryFunction.remove(self.userIndepVars[bCond.side // 2])
                indepVarsForBoundaryFunction.extend(['t'])
                
                if not isinstance(bCond, Connection):
                    bCond.createSpecialProperties(parser, self.params, indepVarsForBoundaryFunction)
                else:
                    bCond.createSpecialProperties(parser, self.params)
    
    def createVertexCondLst(self, totalBCondLst):
        #Составляет список условий на углы блока. Одно условие - это массив из трех граничных условий
        #В эту функцию передаются условия с уже распарсенными значениями
        blockVertexes = ['024', '124', '034', '134', '025', '125', '035', '135']
        listOfConditionsForVertexes = []
        
        for vertex in blockVertexes:
            conditionForVertex = []
            for BCondLst in totalBCondLst:
                for bCond in BCondLst:
                    if vertex in bCond.vertexes:
                        conditionForVertex.append(bCond)
                        break
                if len(conditionForVertex) == 3:
                    listOfConditionsForVertexes.append(conditionForVertex)
                    break
                
        return listOfConditionsForVertexes
    
    def generateVertexFunctions(self, blockNumber, arrWithFunctionNames, parsedVertexCondList):
        # parsedVertexCondList --- это список троек [[условие 1, условие 2, условие 3], [условие 1, условие 2, условие 3], ...]
        output = list()
        icsvCounter = 0
        for vertexCond in parsedVertexCondList:
            parsedEqs = vertexCond[0].parsedEquation
            unknownVars = vertexCond[0].unknownVars
            
            bName1 = determineNameOfBoundary(vertexCond[0].side)
            bName2 = determineNameOfBoundary(vertexCond[1].side)
            bName3 = determineNameOfBoundary(vertexCond[2].side)
            funcIndex = str(vertexCond[0].side) + '_' + str(vertexCond[1].side) + '_' + str(vertexCond[2].side) + '__Eqn' + str(vertexCond[0].equationNumber)
            if not isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection) and not isinstance(vertexCond[2], Connection):
                if vertexCond[0].boundNumber == vertexCond[1].boundNumber == vertexCond[2].boundNumber == -1:
                    output.append('//Default boundary condition for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[0].btype == vertexCond[1].btype == vertexCond[2].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'Neumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                elif vertexCond[0].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
                elif vertexCond[1].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[2])])
#             elif isinstance(angleCond[0], Connection) and not isinstance(angleCond[1], Connection):
#                 if angleCond[1].boundNumber == -1:
#                     output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
#                 output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                 if angleCond[1].btype == 1:
#                     nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                 else:
#                     nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[1])])
#             elif not isinstance(angleCond[0], Connection) and isinstance(angleCond[1], Connection):
#                 if angleCond[0].boundNumber == -1:
#                     output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
#                 output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                 if angleCond[0].btype == 1:
#                     nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                 else:
#                     nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[0])])
#             else:
#                 output.append('//Interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                 nameForVertex = 'Block' + str(blockNumber) + 'Interconnect__Vertex' + funcIndex
#                 output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                 icsvCounter += 1
            
            arrWithFunctionNames.append(nameForVertex)
        return ''.join(output)

    def createRibCondLst(self, totalBCondLst):
        #Формирует всевозможные условия на ребра (пары граничных условий) вместе с одномерными координатами (относительно ребра)
        #области, на которой каждое условие задано
        #В эту функцию передаются условия с уже распарсенными значениями
        blockRibs = {'04': [], '05': [], '14': [], '15': [], '02': [], '03': [], '12': [], '13': [], '24': [], '25': [], '34': [], '35': []}
        #Этот словарь задает соответствие вида {'сторона': индекс массива граничных условий в массиве totalBCondLst}
        correspondenceBetweenIndicesAndSides = {'4': 0, '5': 1, '2': 2, '3': 3, '0': 4, '1': 5}
        for rib in blockRibs:
            fSide = rib[0]
            sSide = rib[1]
            fIdx = correspondenceBetweenIndicesAndSides[fSide]
            sIdx = correspondenceBetweenIndicesAndSides[sSide]
            conditionsOnFirstSide = []
            conditionsOnSecondSide = []
            for bCond in totalBCondLst[fIdx]:
                if rib in bCond.ribs:
                    conditionsOnFirstSide.append(bCond)
            for bCond in totalBCondLst[sIdx]:
                if rib in bCond.ribs:
                    conditionsOnSecondSide.append(bCond)
            blockRibs[rib] = self.determineAllPairsOfConditionsForRib(conditionsOnFirstSide, conditionsOnSecondSide, rib)
        return blockRibs
    
    def determineAllPairsOfConditionsForRib(self, conditionsOnFirstSide, conditionsOnSecondSide, rib):
        #Функция создает условие на ребро (= пара граничных условий) + одномерные координаты места, на котором оно задано
        allPairs = []
        for condition1 in conditionsOnFirstSide:
            for condition2 in conditionsOnSecondSide:
                segment1 = condition1.ribs[rib]
                segment2 = condition2.ribs[rib]
                intersection = self.segmentsIntersects(segment1, segment2)
                if len(intersection) == 0:
                    continue
                allPairs.append((condition1, condition2, intersection))   
        return allPairs
    
    def generateRibsFunctions(self, block, blockNumber, arrWithFunctionNames, parsedRibCondList):
        #Генерирует все функции для всех ребер, создает словарь типа blockFunctionMap, где для каждого ребра указан список,
        #состоящий из списков вида [№ функции, границы]
        output = list()
        #icsvCounter = 0
        for rib in parsedRibCondList:
            boundAndEquatNumberList = []
            listOfConditionsForRib = []
            for ribCond in parsedRibCondList[rib]:
                parsedEqs = ribCond[0].parsedEquation
                unknownVars = ribCond[0].unknownVars
                ranges1D = ribCond[2]
                ranges3D = self.determine3DCoordinatesForCondOnRib(block, ranges1D, rib)
                ranges = getRanges([ranges3D[0], ranges3D[1], self.gridStep[0], block.sizeX], [ranges3D[2], ranges3D[3], self.gridStep[1], block.sizeY], [ranges3D[4], ranges3D[5], self.gridStep[2], block.sizeZ])
                
                boundaryName1 = determineNameOfBoundary(ribCond[0].side)
                boundaryName2 = determineNameOfBoundary(ribCond[1].side)
                if ribCond[0].boundNumber == -1:
                    fBCond = 'Def'
                else:
                    fBCond = str(ribCond[0].boundNumber)
                if ribCond[1].boundNumber == -1:
                    sBCond = 'Def'
                else:
                    sBCond = str(ribCond[1].boundNumber)
                funcIndex = str(ribCond[0].side) + '_' + str(ribCond[1].side) + '__Eqn' + str(ribCond[0].equationNumber) + '__FBCond' + fBCond + '__SBCond' + sBCond
                if not isinstance(ribCond[0], Connection) and not isinstance(ribCond[1], Connection):
                    if ribCond[0].boundNumber == ribCond[1].boundNumber == -1:
                        nameForRib = 'Block' + str(blockNumber) + 'DefaultNeumann__Rib' + funcIndex
                        if (ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
                            continue
                        boundAndEquatNumberList.append((ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber))
                        output.append('//Default boundary condition for Rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                        output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForRib, parsedEqs, unknownVars, [ribCond[0], ribCond[1]])])
                        arrWithFunctionNames.append(nameForRib)
                        listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
                        continue
                    output.append('//Non-default boundary condition for Rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    if ribCond[0].btype == ribCond[1].btype == 1:
                        nameForRib = 'Block' + str(blockNumber) + 'Neumann__Rib' + funcIndex
                        if (ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
                            continue
                        boundAndEquatNumberList.append((ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber))
                        output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForRib, parsedEqs, unknownVars, [ribCond[0], ribCond[1]])])
                    elif ribCond[0].btype == 0:
                        nameForRib = 'Block' + str(blockNumber) + 'Dirichlet__Rib' + funcIndex
                        if (ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
                            continue
                        boundAndEquatNumberList.append((ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForRib, ribCond[0])])
                    else:
                        nameForRib = 'Block' + str(blockNumber) + 'Dirichlet__Rib' + funcIndex
                        if (ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
                            continue
                        boundAndEquatNumberList.append((ribCond[0].boundNumber, ribCond[1].boundNumber, ribCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForRib, ribCond[1])])
#                 elif isinstance(angleCond[0], Connection) and not isinstance(angleCond[1], Connection):
#                     if angleCond[1].boundNumber == -1:
#                         output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                         nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                         arrWithFunctionNames.append(nameForVertex)
#                         continue
#                     output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                     if angleCond[1].btype == 1:
#                         nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                     else:
#                         nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[1])])
#                 elif not isinstance(angleCond[0], Connection) and isinstance(angleCond[1], Connection):
#                     if angleCond[0].boundNumber == -1:
#                         output.append('//Default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                         nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                         arrWithFunctionNames.append(nameForVertex)
#                         continue
#                     output.append('//Non-default boundary condition and interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                     if angleCond[0].btype == 1:
#                         nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                     else:
#                         nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
#                         output.extend([self.generateDirichlet(blockNumber, nameForVertex, angleCond[0])])
#                 else:
#                     output.append('//Interconnect for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'Interconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, angleCond)])
#                     icsvCounter += 1
                
                arrWithFunctionNames.append(nameForRib)
                listOfConditionsForRib.append([arrWithFunctionNames.index(nameForRib)] + ranges)
            parsedRibCondList[rib] = listOfConditionsForRib
        return ''.join(output)
    
    def determine3DCoordinatesForCondOnRib(self, block, condRangesOnRib, rib):
        if rib == '04':
            return [0, 0, condRangesOnRib[0], condRangesOnRib[1], 0, 0]
        elif rib == '05':
            return [0, 0, condRangesOnRib[0], condRangesOnRib[1], block.sizeZ, block.sizeZ]
        elif rib == '14':
            return [block.sizeX, block.sizeX, condRangesOnRib[0], condRangesOnRib[1], 0, 0]
        elif rib == '15':
            return [block.sizeX, block.sizeX, condRangesOnRib[0], condRangesOnRib[1], block.sizeZ, block.sizeZ]
        elif rib == '02':
            return [0, 0, 0, 0, condRangesOnRib[0], condRangesOnRib[1]]
        elif rib == '03':
            return [0, 0, block.sizeY, block.sizeY, condRangesOnRib[0], condRangesOnRib[1]]
        elif rib == '12':
            return [block.sizeX, block.sizeX, 0, 0, condRangesOnRib[0], condRangesOnRib[1]]
        elif rib == '13':
            return [block.sizeX, block.sizeX, block.sizeY, block.sizeY, condRangesOnRib[0], condRangesOnRib[1]]
        elif rib == '24':
            return [condRangesOnRib[0], condRangesOnRib[1], 0, 0, 0, 0]
        elif rib == '34':
            return [condRangesOnRib[0], condRangesOnRib[1], block.sizeY, block.sizeY, 0, 0]
        elif rib == '25':
            return [condRangesOnRib[0], condRangesOnRib[1], 0, 0, block.sizeZ, block.sizeZ]
        elif rib == '35':
            return [condRangesOnRib[0], condRangesOnRib[1], block.sizeY, block.sizeY, block.sizeZ, block.sizeZ]
     
    def segmentsIntersects(self, segment1, segment2):
        intersection = [max([segment1[0], segment2[0]]), min([segment1[1], segment2[1]])]
        if intersection[0] >= intersection[1]:
            return []
        else:
            return intersection
    