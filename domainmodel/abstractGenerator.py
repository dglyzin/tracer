# -*- coding: utf-8 -*-
'''
Created on 11 авг. 2015 г.

@author: golubenets
'''
from equationParser import MathExpressionParser
from someFuncs import generateCodeForMathFunction
from rhsCodeGenerator import RHSCodeGenerator
from someFuncs import getCellCountAlongLine

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
            
    def setEdgesAndVertexesIn3D(self, edges, vertexes):
        self.edges = edges
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
            
    def setEdgesAndVertexesIn3D(self, edges, vertexes):
        self.edges = edges
        self.vertexes = vertexes
        
    def setSecondaryBlockIdx(self, secondaryBlockIdx):
        self.secondaryBlockIdx = secondaryBlockIdx

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
        
class InterconnectRegion3D:
    def __init__(self, firstIndex, secondIndex, side, xfrom, xto, yfrom, yto, zfrom, zto, secondaryBlockNumber):
        self.firstIndex = firstIndex
        self.secondIndex = secondIndex
        self.side = side
        self.xfrom = xfrom
        self.xto = xto
        self.yfrom = yfrom
        self.yto = yto
        self.zfrom = zfrom
        self.zto = zto
        self.secondaryBlockNumber = secondaryBlockNumber
    
class AbstractGenerator(object):
# Генерирует выходную строку для записи в файл
    def __init__(self, delay_lst, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamsIndex):
        self.delay_lst = delay_lst
        self.maxDerivOrder = maxDerivOrder
        self.haloSize = haloSize
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
                #countList.append(int(sizeForIndepVar / d))
                countList.append(getCellCountAlongLine(sizeForIndepVar, d) )                                
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
                function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equationRightHandSide, self.userIndepVars, variables, self.params, list(), self.delay_lst)])
            function.extend(['}\n\n'])
        
        return ''.join(function), arrWithFuncNames

    def generateFunctionSignature(self, blockNumber, name, strideList):
        signatureStart = 'void ' + name + '(double* result, double** source, double t,'
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
    
    def parseBoundaryConditions(self, totalBCondLst, parser):
        #Парсит краевые условия и создает список условий на углы (vertexCondList) 
        for bCondListForSide in totalBCondLst:  
            for bCond in bCondListForSide:
                indepVarsForBoundaryFunction = list(self.userIndepVars)
                indepVarsForBoundaryFunction.remove(self.userIndepVars[bCond.side // 2])
                indepVarsForBoundaryFunction.extend(['t'])
                
                if not isinstance(bCond, Connection):
                    bCond.createSpecialProperties(parser, self.params, indepVarsForBoundaryFunction)
                else:
                    bCond.createSpecialProperties(parser, self.params)
    
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
            function.extend([b.generateRightHandSideCode(blockNumber, unknownVars[i], equation, self.userIndepVars, unknownVars, self.params, pBCL, list())])
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