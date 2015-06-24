# -*- coding: utf-8 -*-
import itertools
from equationParser import MathExpressionParser
from someFuncs import generateCodeForMathFunction, determineNameOfBoundary
from rhsCodeGenerator import RHSCodeGenerator

class FunctionCodeGenerator:
# Генерирует выходную строку для записи в файл
    def __init__(self, equations, blocks, initials, bounds, gridStep):
        varsSet = set([])
        for equation  in equations:
            varsSet.add(tuple(equation.vars))
        if len(varsSet) != 1:
            raise AttributeError("All systems should has the same set of independet variables!")
        
        self.userIndepVars = equations[0].vars
        self.dimension = len(self.userIndepVars)
        self.defaultIndepVars = ['x','y','z']
        self.params = equations[0].params
        self.paramValues = equations[0].paramValues
        if len(self.paramValues) == 1:
            self.defaultParamsIndex = 0
        elif len(self.paramValues) > 1:
            self.defaultParamsIndex = equations.defaultParamsIndex
        self.system = equations[0].system
        
        self.blocks = blocks
        self.initials = initials
        self.bounds = bounds
        self.gridStep = gridStep
        
        cellsizeList = list()
        allBlocksSizeList = list()
        allBlocksOffsetList = list()
        for block in self.blocks:
#             Количество уравнений системы --- как раз и есть cellsize
            cellsizeList.append(len(equations[block.defaultEquation].system))
            if self.dimension == 1:
                allBlocksSizeList.append([block.sizeX,0,0])
                allBlocksOffsetList.append([block.offsetX,0,0])
            elif self.dimension == 2:
                allBlocksSizeList.append([block.sizeX,block.sizeY,0])
                allBlocksOffsetList.append([block.offsetX,block.offsetY,0])
            else: 
                allBlocksSizeList.append([block.sizeX,block.sizeY,block.sizeZ])
                allBlocksOffsetList.append([block.offsetX,block.offsetY,block.offsetZ])
        
        self.cellsizeList = cellsizeList
        self.allBlockSizeList = allBlocksSizeList
        self.allBlockOffsetList = allBlocksOffsetList
        
    def generateAllFunctions(self):
#         Важный момент: всегда предполагается, что массив equations содержит только 1 уравнение.
#         gridStep --- список [gridStepX, gridStepY, gridStepZ]
        outputStr = '#include <math.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include "../hybriddomain/doc/userfuncs.h"\n\n'
        outputStr += self.generateAllDefinitions()
        outputStr += self.generateInitials()
        
        totalArrWithFunctionNames = list()
        functionMaps = []
        for blockNumber, block in enumerate(self.blocks):
            cf = self.generateCentralFunctionCode(block, blockNumber)
#             Этот массив потом будет использован для генерирования функции-заполнителя 
            if self.dimension == 1:
                arrWithFunctionNames = ["Block" + str(blockNumber) + "CentralFunction"]
            elif self.dimension == 2:
                arrWithFunctionNames = ["Block" + str(blockNumber) + "CentralFunction",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex0_2",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex1_2",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex0_3",
                                        "Block" + str(blockNumber) + "DefaultNeumannBoundForVertex1_3"]
            
            blockRanges, boundaryConditionList = self.__getBlockInfo(block, blockNumber)
            bf, blockFunctionMap  = self.generateBoundsAndIcs(blockNumber, arrWithFunctionNames, blockRanges, boundaryConditionList)
            
            totalArrWithFunctionNames.append(arrWithFunctionNames)
            functionMaps.append(blockFunctionMap)
            outputStr += cf + bf
            
        final = self.__generateGetBoundFuncArray(totalArrWithFunctionNames)
        outputStr += final
         
        return outputStr , functionMaps

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
            definitions.append('\n#define Block' + str(blockNumber) + 'CELLSIZE' + ' ' + str(cellsize) + '\n\n')
            for (indepVar, stride, count, offset) in zip(self.defaultIndepVars, strideList, countList, offsetList):
                definitions.append('#define Block' + str(blockNumber) + 'Stride' + indepVar.upper() + ' ' + str(stride) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Count' + indepVar.upper() + ' ' + str(count) + '\n')
                definitions.append('#define Block' + str(blockNumber) + 'Offset' + indepVar.upper() + ' ' + str(offset) + '\n')
        definitions.append("\n#define PAR_COUNT " + str(len(self.params)) + "\n\n")

        return ''.join(definitions)

    def generateInitials(self):
#         initials --- массив [{"Name": '', "Values": []}, {"Name": '', "Values": []}]
        output = list(["//===================PARAMETERS==========================//\n\n"])
        output.append(self.__generateParamFunction())
        output.append("//===================INITIAL CONDITIONS==========================//\n\n")

        pointInitials, listWithInitialFunctionNames, listWithDirichletFunctionNames = self.__generateAllPointInitials()
        output.append(pointInitials)
        output.append(self.__generateFillInitValFuncsForAllBlocks(listWithInitialFunctionNames, listWithDirichletFunctionNames))
        output.append(self.__generateGetInitFuncArray())
        
        return ''.join(output)                     

    def __generateParamFunction(self):
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
    
    def __generateAllPointInitials(self):
#         Генерирует все точечные начальные функции и возвращает строку из них; возвращает массив, содержащий имена начальных функций и
#         массив, содержащий имена граничных функций Дирихле.
#         Индекс в этом массиве имени каждой сгенерированной начальной функции совпадает с индексом соответствующего начального условия
#         в массиве файла .json
#         Все для начальных условий
        countOfEquations = len(self.system)
        parser = MathExpressionParser()
        allFunctions = list()
        listWithInitialFunctionNames = list()
        for initialNumber, initial in enumerate(self.initials):
            pointFunction = list()
            valueList = initial.values
            if len(valueList) != countOfEquations:
                raise AttributeError("Component's count of some initial condition is not corresponds to component's count of unknown vector-function!")      
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
                if len(valueList) != countOfEquations:
                    raise AttributeError("Component's count of some boundary condition is not corresponds to component's count of unknown vector-function!")      
                name = "DirichletInitial" + str(boundNumber)
                listWithDirichletFunctionNames.append(name)
                pointFunction.append("void " + name + "(double* cellstart, double x, double y, double z){\n")
                
                indepVarsForInitialFunction = self.userIndepVars + ['t']
                for k,value in enumerate(valueList):
                    parsedInitial = parser.parseMathExpression(value, self.params, indepVarsForInitialFunction)
                    parsedInitialAfterReplacing = self.__replaceTimeToZeroInInitialCondition(parsedInitial)
                    newValue = generateCodeForMathFunction(parsedInitialAfterReplacing, self.userIndepVars, indepVarsForInitialFunction)
                    pointFunction.append("\tcellstart[" + str(k) + "] = " + newValue + ";\n")
                pointFunction.append("}\n\n")
                allFunctions.append(''.join(pointFunction))
            else:
                listWithDirichletFunctionNames.append("empty")
        return ''.join(allFunctions), listWithInitialFunctionNames, listWithDirichletFunctionNames
    
    def __replaceTimeToZeroInInitialCondition(self, DirichletConditionForParsing):
#         Заменяет в условии Дирихле, которое хотим сделать начальным условием, переменную t на 0.0;
#         DirichletConditionForParsing -- функция, в которой выполняется замена. Она здесь -- в виде массива лексем уже.
        operations = ['+','-','*','/']
        prevOperationsAndBoundaries = operations + ['(']
        postOperationsAndBoundaries = operations + [')']
        lastIndexInList = len(DirichletConditionForParsing) - 1
        for idx,element in enumerate(DirichletConditionForParsing):
            if element == 't':
                doReplace = False
#                 Если в строке стоит лишь 't'
                if lastIndexInList == 0:
                    return '0.0'
                else:
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
    
    def __generateFillInitValFuncsForAllBlocks(self,listWithInitialFunctionNames, listWithDirichletFunctionNames):
#         Для каждого блока создает функцию-заполнитель с именем BlockIFillInitialValues (I-номер блока)
        totalCountOfInitials = len(listWithInitialFunctionNames)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
#              Для данного блока определяется список индексов начальных функций в массиве listWithInitialFunctionNames
            defaultInitialIndex = block.defaultInitial
            listOfInitialIndices = list([defaultInitialIndex])
            for initialRegion in block.initialRegions:
                if initialRegion.initialNumber >= totalCountOfInitials:
                    raise AttributeError("Number of initial condition in some initial region of some block shouldn't be greater or equal to count of initials!")
                if initialRegion.initialNumber != defaultInitialIndex:
                    listOfInitialIndices.append(initialRegion.initialNumber)
            countOfInitialsForBlock = len(listOfInitialIndices)
#              Для данного блока определяется список индексов функций Дирихле в массиве listWithDirichletFunctionNames            
            setOfDirichletIndices = set([])
            countOfBoundaries = len(self.bounds)
            for boundRegion in block.boundRegions:
                boundNumber = boundRegion.boundNumber
                if boundNumber >= countOfBoundaries:
                    raise AttributeError("In some of bound regions the value of bound number greater or equal to count of boundaries!")
                if self.bounds[boundNumber].btype == 0 and boundNumber not in setOfDirichletIndices:
                    setOfDirichletIndices.add(boundNumber)
            countOfDirichletForBlock = len(setOfDirichletIndices)
#             Генерируется сама функция-заполнитель.
            fillFunction = list()
            strBlockNum = str(blockNumber)
            signature = "void Block" + strBlockNum + "FillInitialValues(double* result, unsigned short int* initType){\n"
            fillFunction.append(signature)
            
            fillFunction.append("\tinitfunc_ptr_t initFuncArray[" + str(countOfInitialsForBlock + countOfDirichletForBlock) + "];\n")
#             Создаем заполнение начальными функциями
            for num, idx in enumerate(listOfInitialIndices):
                number = str(num)
                fillFunction.append("\tinitFuncArray[" + number + "] = " + listWithInitialFunctionNames[idx] + ";\n")
#             Создаем заполнение функциями Дирихле
            for num1, idx1 in enumerate(setOfDirichletIndices):
                number1 = str(countOfInitialsForBlock + num1)
                fillFunction.append("\tinitFuncArray[" + number1 + "] = " + listWithDirichletFunctionNames[idx1] + ";\n")
            
#             В зависимости от размерности блока генерируется 1, 2 или 3 цикла for
            if self.dimension == 3:
                fillFunction.append("\tfor(int idxZ = 0; idxZ<Block" + strBlockNum + "CountZ; idxZ++)\n")
                fillFunction.append("\t\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n")
                fillFunction.append("\t\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
                spaces = "\t\t\t\t"
                idx = "int idx = (idxZ*Block" + strBlockNum + "CountY*Block" + strBlockNum + "CountX + idxY*Block" + strBlockNum + "CountX + idxX)*Block" + strBlockNum + "CELLSIZE;\n"
                params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, Block" + strBlockNum + "OffsetZ + idxZ*DZ"  
            elif self.dimension == 2:
                fillFunction.append("\tfor(int idxY = 0; idxY<Block" + strBlockNum + "CountY; idxY++)\n")
                fillFunction.append("\t\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
                spaces = "\t\t\t"
                idx = "int idx = (idxY*Block" + strBlockNum + "CountX + idxX)*Block" + strBlockNum + "CELLSIZE;\n"
                params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, Block" + strBlockNum + "OffsetY + idxY*DY, 0"
            else:
                fillFunction.append("\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n")
                spaces = "\t\t"
                idx = "int idx = idxX*Block" + strBlockNum + "CELLSIZE;\n"
                params = "result+idx, Block" + strBlockNum + "OffsetX + idxX*DX, 0, 0"
            fillFunction.append(spaces + idx)
            fillFunction.append(spaces + "int type = initType[idx];\n")
            fillFunction.append(spaces + "initFuncArray[type](" + params + ");}\n")
            fillFunction.append("}\n\n")
            allFillFunctions.append(''.join(fillFunction))
        return ''.join(allFillFunctions)
    
    def __generateGetInitFuncArray(self):
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
    
    def generateCentralFunctionCode(self, block, blockNumber):
#         defaultIndepVars отличается лишь количеством элементов userIndepVars, т.к. считаем, что переменные могут называться только x,y,z.
        function = list([])
        function.extend(['\n//=========================CENTRAL FUNCTION FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'])
        strideList = list([])
#         Здесь используется defaultIndepVrbls, потому что договорились генерировать сигнатуры функций с одинаковым количеством параметров.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function.extend(['//Central function for '+str(len(self.userIndepVars))+'d model for block with number ' + str(blockNumber) + '\n'])    
        function.extend(self.__generateFunctionSignature(blockNumber, 'Block' + str(blockNumber) + 'CentralFunction', strideList))
            
        parser = MathExpressionParser()
        variables = parser.getVariableList(self.system)
        
#         Во все парсеры необходимо передавать именно userIndepVars!
        b = RHSCodeGenerator()    
        for i,equationString in enumerate(self.system):
            equationRightHandSide = parser.parseMathExpression(equationString, variables, self.params, self.userIndepVars)
            function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equationRightHandSide, self.userIndepVars, variables, self.params)])
        function.extend(['}\n'])
        
        return ''.join(function) + '\n'

    def __generateFunctionSignature(self, blockNumber, name, strideList):
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
    
    def __getBlockInfo(self, block, blockNumber):
# Возвращает границы блока и особый список всех граничных условий
# Offset -- это смещение блока, Size -- длина границы, поэтому границы блока -- это [Offset, Offset + Size]
        minRanges = [block.offsetX]
        maxRanges = [block.offsetX + block.sizeX]
        if self.dimension >= 2:
            minRanges = minRanges + [block.offsetY]
            maxRanges = maxRanges + [block.offsetY + block.sizeY]
        if self.dimension == 3:
            minRanges = minRanges + [block.offsetZ]
            maxRanges = maxRanges + [block.offsetZ + block.sizeZ]
        blockRanges = dict({'min' : minRanges, 'max' : maxRanges})
# boundaryConditionList -- это [{'values':[], 'type':тип, 'side':номер границы, 'boundNumber': номер условия, 'ranges':[[xFrom,xTo],[y],[z]]}]
        boundaryConditionList = list()
        for region in block.boundRegions:
            if region.boundNumber >= len(self.bounds):
                raise AttributeError("Non-existent number of boundary condition is set for some boundary region in array 'Blocks'!")
            side = region.side
            
            if self.dimension == 1:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX]]
                else:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX]]
            elif self.dimension == 2:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX], [region.yfrom, region.yto]]
                elif side == 1:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX], [region.yfrom, region.yto]]
                elif side == 2:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY, block.offsetY]]
                else:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY + block.sizeY, block.offsetY + block.sizeY]]
            else:
                if side == 0:
                    boundaryRanges = [[block.offsetX, block.offsetX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
                elif side == 1:
                    boundaryRanges = [[block.offsetX + block.sizeX, block.offsetX + block.sizeX], [region.yfrom, region.yto], [region.zfrom, region.zto]]
                elif side == 2:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY, block.offsetY], [region.zfrom, region.zto]]
                elif side == 3:
                    boundaryRanges = [[region.xfrom, region.xto], [block.offsetY + block.sizeY, block.offsetY + block.sizeY], [region.zfrom, region.zto]]
                elif side == 4:
                    boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ, block.offsetZ]]
                elif side == 5:
                    boundaryRanges = [[region.xfrom, region.xto], [region.yfrom, region.yto], [block.offsetZ + block.sizeZ, block.offsetZ + block.sizeZ]]

            bound = self.bounds[region.boundNumber]
            #Если условие Дирихле, то используем производные по t,
            #если Неймановское условие --- то сами значения.
            if bound.btype == 0:
                values = bound.derivative
            elif bound.btype == 1:
                values = bound.values
#                 Исправление понятия Неймановского условия
                if side == 0 or side == 2 or side == 4:
                    for idx, value in enumerate(values):
                        values.pop(idx)
                        values.insert(idx, '-(' + value + ')')
            outputValues = list(values)    
            boundaryCondition = {'values': outputValues, 'type': bound.btype, 'side': side, 'boundNumber': region.boundNumber, 'ranges': boundaryRanges}
            boundaryConditionList.append(boundaryCondition)
        return blockRanges, boundaryConditionList
     
    def generateBoundsAndIcs(self, blockNumber, arrWithFunctionNames, blockRanges, boundaryConditionList):
        outputFile = list(self.generateDefaultBoundaryFunction(blockNumber))
        intro = '\n//=============================OTHER BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' + str(blockNumber) + '======================//\n\n'
        outputFile.append(intro)
        parser = MathExpressionParser()
        variables = parser.getVariableList(self.system)
        
        parsedEstrList = list([])
        for equation in self.system:
            parsedEstrList.extend([parser.parseMathExpression(equation, variables, self.params, self.userIndepVars)])
        
        numberOfVariables = len(variables)
        for boundaryCondition in boundaryConditionList:
            if len(boundaryCondition['values']) != numberOfVariables:
                raise SyntaxError("The dimension of unknow vector-function is " + str(numberOfVariables) + ", but one of the input boundary conditions has other number of components!")
        
        sideList = list([])
        parsedBoundaryConditionDictionary = dict({})
        boundaryCount = len(self.userIndepVars) * 2
        #Этот словарь будет помогать правильно нумеровать сишные функции
        countOfGeneratedFunction = dict({})
        for boundaryCondition in boundaryConditionList:
            
            side = boundaryCondition['side']
            boundNumber = boundaryCondition['boundNumber']
            if side in countOfGeneratedFunction:
                countOfGeneratedFunction[side] += 1
            else:
                countOfGeneratedFunction.update({side: 0})
                
            coordList = boundaryCondition['ranges']
            #Если случай двумерный, то формируем координаты отрезков, если трехмерный -- то координаты углов прямоугольника
            boundaryCoordList = self.__createBoundaryCoordinates(coordList)
            
            if side >= boundaryCount:
                raise AttributeError("Error in boundary conditions entry: a value for the key 'side' shouldn't be greater than number of block boundaries!")
            indepVarsForBoundaryFunction = list(self.userIndepVars)
            indepVarsForBoundaryFunction.remove(self.userIndepVars[side // 2])
            indepVarsForBoundaryFunction.extend(['t'])
            
            parsedBoundaryCondition = list([])
            for boundary in boundaryCondition['values']:
                parsedBoundaryCondition.extend([parser.parseMathExpression(boundary, self.params, indepVarsForBoundaryFunction)])
            
            if side in parsedBoundaryConditionDictionary:
                parsedBoundaryConditionDictionary[side].append((parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type'], boundNumber))
            else:
                sideList.extend([side])
                parsedBoundaryConditionDictionary.update({side : [(parsedBoundaryCondition, boundaryCoordList, boundaryCondition['type'], boundNumber)]})
        
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
            if side in parsedBoundaryConditionDictionary:
                counter = 0
                #Это список номеров граничных условий для данной стороны side. Нужен для исключения повторяющихся функций,
                #т.к. на одну сторону в разных местах м.б. наложено одно и то же условие
                boundNumberList = list()
                for condition in parsedBoundaryConditionDictionary[side]:
                    #Если для граничного условия с таким номером функцию еще не создавали, то создать, иначе - не надо.
                    if condition[3] not in boundNumberList:
                        boundNumberList.append(condition[3])
                        parsedBoundaryConditionTuple = list([tuple((side, condition[0]))])
                        if self.dimension == 1 or self.dimension == 2:
                            outputFile.append('//Non-default boundary condition for boundary ' + boundaryName + '\n')
                            if condition[2] == 0:
                                name = 'Block' + str(blockNumber) + 'DirichletBound' + str(side) + '_' + str(counter)
                                outputFile.append(self.__generateDirichlet(blockNumber, name,parsedBoundaryConditionTuple))
                                arrWithFunctionNames.append(name)
                            else:
                                name = 'Block' + str(blockNumber) + 'NeumannBound' + str(side) + '_' + str(counter)
                                outputFile.append(self.__generateNeumann(blockNumber, name, parsedEstrList, variables, parsedBoundaryConditionTuple))
                                arrWithFunctionNames.append(name)
                            sideMap.update({"userBound"+str(condition[3]):bfmLen})
                            bfmLen += 1
                        elif self.dimension == 3:
                            raise AttributeError("Three-dimensional case!")
                        counter += 1
            
            blockFunctionMap.update({sideName:sideMap}) 
            
        
        outputFile.extend(self.__generateVertexAndRibFunctions(blockNumber, arrWithFunctionNames, blockRanges, parsedEstrList, variables, parsedBoundaryConditionDictionary))
        return ''.join(outputFile), blockFunctionMap
    
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
    
    def generateDefaultBoundaryFunction(self, blockNumber):
        defaultFunctions = list()
        parser = MathExpressionParser()
        variables = parser.getVariableList(self.system)
             
        parsedEstrList = list([])
        for equation in self.system:
            parsedEstrList.extend([parser.parseMathExpression(equation, variables, self.params, self.userIndepVars)])
             
        defuaultBoundaryConditionValues = len(variables) * ['0.0']
        
        intro = '\n//=========================DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER ' +str(blockNumber)+'========================//\n\n'       
        defaultFunctions.append(intro)
                 
        boundaryCount = len(self.userIndepVars) * 2
        for i in range(0,boundaryCount):
            boundaryName = determineNameOfBoundary(i)
            defaultFunctions.append('//Default boundary condition for boundary ' + boundaryName + '\n')
            nameForSide = 'Block' + str(blockNumber) + 'DefaultNeumannBound' + str(i)
            defaultBoundaryConditionList = list([tuple((i, defuaultBoundaryConditionValues))])
            defaultFunctions.append(self.__generateNeumann(blockNumber, nameForSide, parsedEstrList, variables, defaultBoundaryConditionList))
# В трехмерном случае нужно для каждого ребра создать функцию по умолчанию, поэтому этот коммент важен             
#         elif len(userIndepVariables) == 3:
#             ribs = [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)]
#             for rib in ribs:
#                 boundaryName1 = determineNameOfBoundary(rib[0])
#                 boundaryName2 = determineNameOfBoundary(rib[1])
#                 defaultFunctions.extend(['//Default boundary condition for rib between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
#                 defaultBoundaryConditionList = list([tuple((rib[0], defuaultBoundaryConditionValues)), tuple((rib[1], defuaultBoundaryConditionValues))])
#                 nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1])
#                 defaultFunctions.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, defaultBoundaryConditionList)])     
        return ''.join(defaultFunctions)
    
    def __generateDirichlet(self, blockNumber, name, parsedBoundaryConditionList):
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
            
        function = self.__generateFunctionSignature(blockNumber, name, strideList)
#         А здесь используем userIndepVariables.        
        indepVarValueList = list([])
        for indepVar in self.userIndepVars:
            indepVarValueList.extend(['idx' + indepVar.upper()])
        indepVarValueList.extend(['t'])
        
        if len(parsedBoundaryConditionList) > 1:
#             Хотя это бред, потому что я хочу использовать эту функцию для генерирования условий на углы и ребра
            raise AttributeError("Error in function __generateDirichlet(): argument 'parsedBoundaryConditionList' should contain only 1 element!")
        for i,boundary in enumerate(parsedBoundaryConditionList[0][1]):
            boundaryExpression = generateCodeForMathFunction(boundary, self.userIndepVars, indepVarValueList)
            result = '\t result[idx + ' + str(i) + '] = ' + boundaryExpression + ';\n'
            function.extend([result])
        function.extend(['}\n'])
        
        return ''.join(function)
        
    def __generateNeumann(self, blockNumber, name, parsedEstrList, variables, parsedBoundaryConditionList): 
#         parsedBoundaryConditionList --- это список, содержащий от 1 до 3 кортежей (Номер границы, РАСПАРСЕННЫЕ граничные условия)
#         parsedEstrList --- список, элементы которого --- распарсенные правые части всех уравнений
        strideList = list([])
#         Здесь используем defaultIndepVariables, т.к. сигнатуры у всех генерируемых функций должны быть одинаковы.
        for indepVar in self.defaultIndepVars:
            strideList.extend(['Block' + str(blockNumber) + 'Stride' + indepVar.upper()])
        
        function = self.__generateFunctionSignature(blockNumber, name, strideList)
        
#         А здесь используем userIndepVariables.
        b = RHSCodeGenerator()
        for i, equation in enumerate(parsedEstrList):
            function.extend([b.generateRightHandSideCode(blockNumber, variables[i], equation, self.userIndepVars, variables, self.params, parsedBoundaryConditionList)])
        function.extend(['}\n'])
        
        return ''.join(function)
        
    def __generateVertexAndRibFunctions(self, blockNumber, arrWithFunctionNames, blockRanges, parsedEstrList, variables, parsedBoundaryConditionDictionary):
#         blockRanges --- это словарь {'min' : [x_min,y_min,z_min], 'max' : [x_max,y_max,z_max]}
#         parsedBoundaryConditionDictionary --- это словарь вида {Номер границы : [(распарсенное условие 1, [4 или 2 координаты краев части 1 границы], Тип условия),
#                                                                                  (распарсенное условие 2, [4 или 2 координаты краев части 2 границы], Тип условия), ...]}
#         В двумерном случае [координаты краев части 1 границы] содержат две точки, а в трехмерном --- четыре
        output = list([])
        
        defuaultBoundaryConditionValues = list([])
        for var in variables:
            defuaultBoundaryConditionValues.extend(['0.0'])
        
        blockDimension = len(self.userIndepVars)
#         Двумерный случай
        if blockDimension == 2:
            Vertexs = [(0,2),(1,2),(0,3),(1,3)]
            VertexsCoordinates = [(blockRanges['min'][0], blockRanges['min'][1]),(blockRanges['max'][0], blockRanges['min'][1]),
                                  (blockRanges['min'][0], blockRanges['max'][1]),(blockRanges['max'][0], blockRanges['max'][1])]
#             Для каждого угла ищутся граничные условия, заданные пользователем. Если находятся, то используются они,
#             а иначе используются дефолтные
            for i,Vertex in enumerate(Vertexs):
                index = i + 1
#                 Делается преобразование в множество потому, что для множеств определена операция isdisjoint()
                c = set([VertexsCoordinates[i]])
                
                bound1CondValue = defuaultBoundaryConditionValues
                bound2CondValue = defuaultBoundaryConditionValues
                type1 = 1
                type2 = 1
                
                if Vertex[0] in parsedBoundaryConditionDictionary:
                    bound1CondList = parsedBoundaryConditionDictionary[Vertex[0]]
                    for boundCondition in bound1CondList:
                        a = set(boundCondition[1])
                        if not a.isdisjoint(c):
                            bound1CondValue = boundCondition[0]
#                             Запоминаем типы условий, чтобы потом генерировать либо Дирихле либо Неймана!
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
                
                boundaryName1 = determineNameOfBoundary(Vertex[0])
                boundaryName2 = determineNameOfBoundary(Vertex[1])
                if bound1CondValue == defuaultBoundaryConditionValues and bound2CondValue == defuaultBoundaryConditionValues:
#                     Генерируется функция для угла по-умолчанию; ничего в массив не записывается, т.к. дефолтное значение уже записано
                    output.extend(['//Default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, boundaryConditionList)])
                    continue
                output.extend(['//Non-default boundary condition for Vertex between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n'])
                if type1 == type2 == 1:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue)), tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
                
                arrWithFunctionNames.pop(index)
                arrWithFunctionNames.insert(index, nameForVertex)
        
#         А в трехмерном случае пока что не учтен массив arrWithFunctionNames       
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
                boundaryName1 = determineNameOfBoundary(rib[0])
                boundaryName2 = determineNameOfBoundary(rib[1])
                pairsOfBoundaryCondition = list()
                if rib[0] in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                    boundary1CondList = parsedBoundaryConditionDictionary[rib[0]]
                    boundary2CondList = parsedBoundaryConditionDictionary[rib[1]]
                    pairsOfBoundaryCondition = self.__algorithmForRib(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundary1CondList, boundary2CondList, defuaultBoundaryConditionValues)
                elif rib[0] in parsedBoundaryConditionDictionary and rib[1] not in parsedBoundaryConditionDictionary:
#                     Здесь надо сначала определить те границы, которые касаются ребра, и для каждой из них
#                     сгенерить функцию
                    for boundaryCondition in parsedBoundaryConditionDictionary[rib[0]]:
                        if len(self.__rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((boundaryCondition[0],boundaryCondition[2]), (defuaultBoundaryConditionValues,1)))
                elif rib[0] not in parsedBoundaryConditionDictionary and rib[1] in parsedBoundaryConditionDictionary:
                    for boundaryCondition in parsedBoundaryConditionDictionary[rib[1]]:
                        if len(self.__rectVertexNearSegment(ribsCoordinates[idx][0], ribsCoordinates[idx][1], boundaryCondition[1])[0]) == 2:
                            pairsOfBoundaryCondition.append(((defuaultBoundaryConditionValues,1), (boundaryCondition[0],boundaryCondition[2])))
                else:
                    continue
                for number,pair in enumerate(pairsOfBoundaryCondition):
                    output.extend(['//Non-default boundary condition for RIB between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + ' with number ' + str(number) + '\n'])
                    if pair[0][1] == pair[1][1] == 1:
                        nameForRib = 'Block' + str(blockNumber) + 'NeumannBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0])), tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateNeumann(blockNumber, nameForRib, parsedEstrList, variables, boundaryConditionList)])
                    elif pair[0][1] == 0:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[0], pair[0][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, boundaryConditionList)])
                    else:
                        nameForRib = 'Block' + str(blockNumber) + 'DirichletBoundForRib' + str(rib[0]) + '_' + str(rib[1]) + '_' + str(number)
                        boundaryConditionList = list([tuple((rib[1], pair[1][0]))])
                        output.extend([self.__generateDirichlet(blockNumber, nameForRib, boundaryConditionList)])
            
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
                    output.extend([self.__generateNeumann(blockNumber, nameForVertex, parsedEstrList, variables, boundaryConditionList)])
                elif type1 == 0:
                    boundaryConditionList = list([tuple((Vertex[0], bound1CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
                elif type2 == 0:
                    boundaryConditionList = list([tuple((Vertex[1], bound2CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])
                else:
                    boundaryConditionList = list([tuple((Vertex[2], bound3CondValue))])
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletBoundForVertex' + str(Vertex[0]) + '_' + str(Vertex[1])
                    output.extend([self.__generateDirichlet(blockNumber, nameForVertex, boundaryConditionList)])

        return output
    
    def __generateGetBoundFuncArray(self, totalArrWithFunctionNames):
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
    
    
    def __rectVertexNearSegment(self, ribCoordinateMin, ribCoordinateMax, rectCoordinateList):
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
    
#     def __computeSideLength2D(self, blockRanges, Side):
# #         blockRanges --- словарь {"min": [x,y,z], "max": [x,y,z]}
# #         side --- номер стороны, длину которой надо вычислить       
#         if Side == 0 or Side == 1:
#             return blockRanges["max"][1] - blockRanges["min"][1]
#         elif Side == 2 or Side == 3:
#             return blockRanges["max"][0] - blockRanges["min"][0]
#         else:
#             raise AttributeError("Side should be 0, 1, 2 or 3!")
#     
#     def __computeSegmentLength2D(self, segment):
# #         segment = [(x1,y1),(x2,y2)]
#         if len(segment) != 2 or len(segment[0]) != 2 or len(segment[1]) != 2:
#             raise AttributeError("List 'segment' in __computeSegmentLength2D() should contain exactly two elements!")
# #         т.к. отрезки параллельны осям кординат, то можно делать так
#         reducedSegment = []
# #         Двумерный случай сводится к одномерному
#         if segment[0][0] == segment[1][0]:
#             reducedSegment = [min([segment[0][1], segment[1][1]]), max([segment[0][1], segment[1][1]])]
#         elif segment[0][1] == segment[1][1]:
#             reducedSegment = [min([segment[0][0], segment[1][0]]), max([segment[0][0], segment[1][0]])]
#             
#         return reducedSegment[1] - reducedSegment[0]
#     
    
#     def __segmentsIntersects(self, segment1, segment2):
# #         segment1, segment2 --- одномерные отрезки, вовсе необязательно, что segmentI[0] <= segmentI[1], I = 1,2!
# #         Делаем так, чтобы в обоих отрезках левая граница была <= правой
#         if len(segment1) != 2 or len(segment2) != 2:
#             raise AttributeError("Lists 'segment1' and 'segment2' in __segmentIntersections() should contain exactly two elements!")
#         if segment1[0] > segment1[1]:
#             segment1.reverse()
#         if segment2[0] > segment2[1]:
#             segment2.reverse()
#         first = segment1[0] >= segment2[0] and segment1[0] <= segment2[1]
#         second = segment1[1] >= segment2[0] and segment1[1] <= segment2[1]
#         third = segment2[1] >= segment1[0] and segment2[1] <= segment1[1]
#         fourth = segment2[0] >= segment1[0] and segment2[0] <= segment1[1]
#         if first or second or third or fourth:
#             return True
#         else:
#             return False
#     
#     def __determineAllPairsOfConditions(self, resultCondList1, resultCondList2, defaultBoundaryConditions):
# #         Для каждого из условий в resultCondList1 ищет все условия из resultCondList2
#         outputConditionList = list()
#         for boundaryCond1 in resultCondList1:
# #             Это список отрезков, пересекающихся с отрезком для boundaryCond1. Друг с другом они не пересекаются,
# #             поэтому их можно упорядочить по левой границе.
#             listOfSegments = list()
# #             Может получится так, что в resultCondList1 лежит хотя бы одно краевое условие,
# #             а в resultCondList2 ничего нет. Тогда надо сгенерить пару с дефолтным краевым условием.
#             if len(resultCondList2) > 0:
#                 for boundaryCond2 in resultCondList2:
#                     if self.__segmentsIntersects(boundaryCond1[3], boundaryCond2[3]):
#                         listOfSegments.extend([boundaryCond2[3]])
#                         outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (boundaryCond2[0],boundaryCond2[4]))])
#     #                 Сортируем массив отрезков по левой границе
#                     listOfSegments.sort(key = lambda lst : lst[0])
#                     length = len(listOfSegments)
#     #                 Идем по всему списку отрезков и если есть хотя бы 2 не касающихся отрезка,
#     #                 то составляем пару (граничное условие, дефолтное граничное условие)
#                     if length > 0:
#                         if listOfSegments[0][0] <= boundaryCond1[3][0] and listOfSegments[length - 1][1] >= boundaryCond1[3][1]:
#                             for i,segment in enumerate(listOfSegments):
#                                 if i < length - 1 and segment[1] < listOfSegments[i+1][0]:
#                                     outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
#                                     break
#                         else:
#                             outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
#                     else:
#                         outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
#             else:
#                 outputConditionList.extend([((boundaryCond1[0],boundaryCond1[4]), (defaultBoundaryConditions,1))])
#         return outputConditionList
#     
#     def __algorithmForRib(self, ribCoordinateMin, ribCoordinateMax, boundary1CondList, boundary2CondList, defaultBoundaryConditions):
# # Функция возвращает список кортежей --- пар условий.
# # ribCoordinateMin = (x,y,z_min), ribCoordinateMax = (x,y,z_max) или x_min x_max или y_min y_max
# # Каждый из списков имеет вид [(распарсенное условие 1, [4 координаты углов части 1 границы], Тип условия),
# #                              (распарсенное условие 2, [4 координаты углов части 2 границы], Тип условия), ...]
# #         Шаг 1: определить все условия, смежные с ребром, на каждой из границ
#         result1CondList = list()
#         result2CondList = list()
# #         Для каждого из списков boundary1CondList и boundary2CondList создали списки условий, котрые смежны с ребром
#         generalResultCondList = list([result1CondList, result2CondList])
#         
#         generalCondList = list([boundary1CondList, boundary2CondList])
#         for (boundaryCondList, resultCondList) in zip(generalCondList, generalResultCondList):
#             for boundaryCondition in boundaryCondList:
#                 pointsOnRib = self.__rectVertexNearSegment(ribCoordinateMin, ribCoordinateMax, boundaryCondition[1])
#                 if len(pointsOnRib[0]) == 2:
# #                     (Сами условия, координаты углов, список координат углов на ребре, координаты одномерного отрезка, Тип условия)
#                     resultCondList.extend([(boundaryCondition[0], boundaryCondition[1], pointsOnRib[0], pointsOnRib[1], boundaryCondition[2])])
#         
# #         Шаг 2: теперь составляем всевозможные пары условий (Условие на 1 границу, условие на 2 границу):
# #         для каждого условия первой границы берем все подходящие условия второй, и наоборот.
# #         Потом их объединяем и возвращаем в виде списка.
#         finalResultCondList1 = self.__determineAllPairsOfConditions(generalResultCondList[0], generalResultCondList[1], defaultBoundaryConditions)
#         finalResultCondList2 = self.__determineAllPairsOfConditions(generalResultCondList[1], generalResultCondList[0], defaultBoundaryConditions)
# #         Надо, чтобы первым элементом кортежа было условие из generalResultCondList[0], поэтому переворачиваем кортежи в finalResultCondList2
#         for idx,pair in enumerate(finalResultCondList2):
#             tmp = list(finalResultCondList2.pop(idx))
#             tmp.reverse()
#             finalResultCondList2.insert(idx, tuple(tmp))
# #         Исключаем из второго списка все пары, которые уже присутствуют в первом списке.
#         for pairTuple in finalResultCondList1:
#             if pairTuple in finalResultCondList2:
#                 finalResultCondList1.remove(pairTuple)
#         a = finalResultCondList1 + finalResultCondList2
#         return a
