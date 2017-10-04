# -*- coding: utf-8 -*-
'''
Created on 11 авг. 2015 г.

@author: golubenets
'''

import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.abstractGenerator import AbstractGenerator, BoundCondition, Connection, InterconnectRegion
    from domainmodel.equationParser import MathExpressionParser
    from domainmodel.someFuncs import determineNameOfBoundary,  squareOrVolume, determineCellIndexOfStartOfConnection2D, getRangesInClosedInterval

else:
    from abstractGenerator import AbstractGenerator, BoundCondition, Connection, InterconnectRegion
    from equationParser import MathExpressionParser
    from someFuncs import determineNameOfBoundary, squareOrVolume, determineCellIndexOfStartOfConnection2D, getRangesInClosedInterval

class Generator2D(AbstractGenerator):
    def __init__(self, delay_lst, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(Generator2D,self).__init__(delay_lst, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
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
            xfrom = 0#mainBlock.offsetX
            xto = 0#mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[1]
        elif mainBlockSide == 1:
            xfrom = mainBlock.sizeX# + mainBlock.offsetX
            xto = mainBlock.sizeX# + mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[1]
        elif mainBlockSide == 2:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = 0#mainBlock.offsetY
            yto = 0#mainBlock.offsetY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[0]
        else:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = mainBlock.sizeY# + mainBlock.offsetY
            yto = mainBlock.sizeY# + mainBlock.offsetY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[0]
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
        '''
        DESCRIPTION:
        Split equations at equations regions for central.
        
        OUTPUT:
        systemsForCentralFuncs - list of equations
 
        numsForSystems - numbers for equation in 
                         systemsForCentralFuncs

        totalBCondLst - list of BoundCondition objects 
                        with equation for each region 
                        (from Bounds and EquationRegions)
                        for each side. 
                        (see createListOfBCondsForSide for more)

        totalInterconnectLst = [] - ?

        blockFuncMap - mapping equations to block parts.
                       like 
                       center: [  [ 1, xfrom, xto, yfrom, yto],
                       means equation[1] for part 
                                         (xfrom, yfrom), (xto, yto)

        USED FUNCTIONS:
        getRangesInClosedInterval
        createListOfBCondsForSide

        USED IN:
        FuncGenerator.generateAllFunctions
        
        '''
        systemsForCentralFuncs = []
        numsForSystems = []
        blockFuncMap = {'center': []}
        blockSquare = block.sizeX * block.sizeY
        reservedSquare = 0

        # split equations at regions
        for eqRegion in block.equationRegions:
            
            # for removing trivial cases
            cond1 = eqRegion.xfrom == eqRegion.xto and (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX)
            cond2 = eqRegion.yfrom == eqRegion.yto and (eqRegion.yto == 0.0 or eqRegion.yto == block.sizeY)

            reservedSquare += squareOrVolume([eqRegion.xfrom, eqRegion.xto],
                                             [eqRegion.yfrom, eqRegion.yto])

            # if We not alredy added equation with number eqRegion.equationNumber  
            if eqRegion.equationNumber not in numsForSystems and not cond1 and not cond2:
                systemsForCentralFuncs.append(self.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)

            if not cond1 and not cond2:
                ranges = getRangesInClosedInterval([eqRegion.xfrom, eqRegion.xto, self.gridStep[0]],
                                                   [eqRegion.yfrom, eqRegion.yto, self.gridStep[1]])
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber)] + ranges)
        
        # add default equation at remaining regions.
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
        '''
        DESCRIPTION:
        Using block.BoundRegions and block.equationRegions to
        create BoundCondition objects list for each side.

        EXAMPLE:
        For block side 2 (y = 0)
        with
        "BoundRegions": [
                {
                    "BoundNumber": 0,  
                    "Side": 2, 
                    "xfrom": 0.25, 
                    "xto": 0.75,
                    "yfrom": 0.0,
                    "yto": 0.0
                }
            ]
        and
        "EquationRegions": [
                {
                    "EquationNumber": 1,
                    "xfrom": 0.4, 
                    "xto": 0.6, 
                    "yfrom": 0.0, 
                    "yto": 0.6
                }]
        return 
        [BoundCondition 
            with ranges = [[0.0, 0.25], [0.0, 0.0]]
                 equation = equation with number 0 (default),
         BoundCondition
            with ranges = [[0.25, 0.4], [0.0, 0.0]]
                 equation = equation with number 0 (default),
         BoundCondition
            with ranges = [[0.4, 0.6], [0.0, 0.0]]
                 equation = equation with number 1,
         BoundCondition
            with ranges = [[0.6, 0.75], [0.0, 0.0]]
                 equation = equation with number 0 (default),
         ] 

        USED FUNCTIONS:
        createListOfBCondsForPartOfSide
        
        '''
        if side == 2:
            cellLen = self.gridStep[0]
            sideMaxRange = block.sizeX
            sideMinRange = 0.0
            currentSideValue = 0.0
            sideIndicator = lambda eqRegion: eqRegion.yfrom
            stepFrom = lambda eqRegion: eqRegion.xfrom
            stepTo = lambda eqRegion: eqRegion.xto
        elif side == 3:
            cellLen = self.gridStep[0]
            sideMaxRange = block.sizeX
            sideMinRange = 0.0
            currentSideValue = block.sizeY
            sideIndicator = lambda eqRegion: eqRegion.yto
            stepFrom = lambda eqRegion: eqRegion.xfrom
            stepTo = lambda eqRegion: eqRegion.xto
        elif side == 0:
            cellLen = self.gridStep[1]
            sideMaxRange = block.sizeY
            sideMinRange = 0.0
            currentSideValue = 0.0
            sideIndicator = lambda eqRegion: eqRegion.xfrom
            stepFrom = lambda eqRegion: eqRegion.yfrom
            stepTo = lambda eqRegion: eqRegion.yto
        elif side == 1:
            cellLen = self.gridStep[1]
            sideMaxRange = block.sizeY
            sideMinRange = 0.0
            currentSideValue = block.sizeX
            sideIndicator = lambda eqRegion: eqRegion.xto
            stepFrom = lambda eqRegion: eqRegion.yfrom
            stepTo = lambda eqRegion: eqRegion.yto
        bCondList = list()    
        var_min = sideMinRange

        # Идем по стороне. Определяем все области, 
        # в которых заданы и дефолтные и недефолтные уравнения.
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

            # Для каждой из таких областей определяем все области,
            # где заданы дефолтные и недефолтные граничные условия.
            bCondList.extend(self.createListOfBCondsForPartOfSide(block, blockNumber,
                                                                  side, ranges,
                                                                  equationNumber, equation,
                                                                  stepFrom, stepTo, cellLen))
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
                    bCondList.extend(self.createListOfBCondsForPartOfSide(block, blockNumber,
                                                                          side, ranges,
                                                                          equationNumber, equation,
                                                                          stepFrom, stepTo, cellLen))
        return bCondList
    
    def createListOfBCondsForPartOfSide(self, block, blockNumber, side, ranges, equationNum, equation, stepFrom, stepTo, cellLen):
        '''
        DESCRIPTION:

        USED IN:
        createListOfBCondsForSide

        USED FUNCTIONS:
        determineCellIndexOfStartOfConnection2D
        setDirichletOrNeuman
        setDefault
        '''
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
                    startCellIndex = determineCellIndexOfStartOfConnection2D(icRegion)
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
                condList.append(BoundCondition(values, btype, side, bCondRanges,
                                               boundNumber, equationNum,
                                               equation, funcName,
                                               block, blockNumber, '2D'))
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
                condList.append(BoundCondition(values, btype, side, bCondRanges,
                                               boundNumber,
                                               equationNum, equation, funcName,
                                               block, blockNumber, '2D'))
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
                    condList.append(BoundCondition(values, btype, side, bCondRanges,
                                                   boundNumber,
                                                   equationNum, equation, funcName,
                                                   block, blockNumber, "2D"))
                elif var_max == var_min or var_max > var_min and conds[1] or conds[2]:
                    if side == 2 or side == 3:
                        bCondRanges = [[var_min, min([stepTo(varMaxReg), max(varRanges)])], secRanges]
                    else:
                        bCondRanges = [secRanges, [var_min, min([stepTo(varMaxReg), max(varRanges)])]]
                    var_min = min([stepTo(varMaxReg), max(varRanges)]) + cellLen * (stepFrom(varMaxReg) == stepTo(varMaxReg))
                    #Если там стоит граничное условие
                    if not isinstance(varMaxReg, InterconnectRegion):
                        values, btype, boundNumber, funcName = self.setDirichletOrNeumann(varMaxReg, blockNumber, side, equationNum)
                        condList.append(BoundCondition(values, btype, side, bCondRanges,
                                                       boundNumber,
                                                       equationNum, equation, funcName,
                                                       block, blockNumber, '2D'))
                    #Если там стоит соединение
                    else:
                        startCellIndex = determineCellIndexOfStartOfConnection2D(varMaxReg)
                        secondIndex = '(' + varMaxReg.secondIndex + ' - ' + str(startCellIndex) + ') * Block' + str(blockNumber) + 'CELLSIZE'
                        funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(varMaxReg.side) + "_Eqn" + str(equationNum) + "_SBlock" + str(varMaxReg.secondaryBlockNumber)
                        condList.append(Connection(varMaxReg.firstIndex, secondIndex, side, bCondRanges, equationNum, equation, funcName))
        return condList
  
    def generateBoundsAndIcs(self, block, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst):
        '''
        DESCRIPTION:
        For each bound choice it method.
        For which vertex or edges this method will be
        used described in cpp function name. 
        (like Block0DefaultNeumannAndInterconnect__Vertex3_0__Eqn0
         for y = y_max and x = 0)
          ***x->
          *  
          |  ---side 2---
          y  |          |
             s          s
             i          i
             d          d
             e          e
             0          1
             |          |
             ---side 3---

        INPUT:
        totalBCondLst - list of Connection or BoundCondition
                        objects, containing values property with
                        function string for bounds equation.
                        (from generator2D.getBlockInfo)
    
        blockFunctionMap -- used for saveDomain

        USED FUNCTIONS:
        parseBoundaryConditions
        createVertexCondLst
        
        generateVertexFunctions
        determineNameOfBoundary
        EquationLieOnSomeBound
        getRangesInClosedInterval

        generateNeumannOrInterconnect
        generateDirichlet

        '''

        # parse boundaries and vertex functions
        parser = MathExpressionParser()
        self.parseBoundaryConditions(totalBCondLst, parser)
        parsedVertexCondList = self.createVertexCondLst(totalBCondLst)

        intro = ('\n//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER '
                 + str(blockNumber)
                 + '======================//\n\n')
        outputStr = [intro]
        outputStr.append(self.generateVertexFunctions(blockNumber, arrWithFunctionNames, parsedVertexCondList))      
        
        #counter for elements in blockFunctionMap including subdictionaries
        bfmLen = len(arrWithFunctionNames)
        #dictionary to return to binarymodel
        blockFunctionMap.update({"v02":bfmLen - 4, "v12":bfmLen - 3, "v03":bfmLen - 2, "v13":bfmLen - 1 })

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
                        # sideLst for saveDomain
                        ranges = getRangesInClosedInterval([condition.ranges[0][0], condition.ranges[0][1],
                                                            self.gridStep[0], block.sizeX],
                                                           [condition.ranges[1][0], condition.ranges[1][1],
                                                            self.gridStep[1], block.sizeY])

                        sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
                        continue
                    boundAndEquatNumbersList.append((condition.boundNumber, condition.equationNumber))

                    outputStr.append('//Boundary condition for boundary ' + boundaryName + '\n')

                    #Если надо сгенерить граничное условие
                    if condition.btype == 0:
                        outputStr.append(self.generateDirichlet(blockNumber, condition.funcName, condition))
                    else:
                        pBCL = [condition]
                        outputStr.append(self.generateNeumannOrInterconnect(blockNumber, condition.funcName,
                                                                            condition.parsedEquation,
                                                                            condition.unknownVars, pBCL))
                #Если надо сгенерить соединение блоков
                else:
                    outputStr.append('//Interconnect for boundary ' + boundaryName + '\n')
                    pBCL = [condition]
                    outputStr.append(self.generateNeumannOrInterconnect(blockNumber, condition.funcName,
                                                                        condition.parsedEquation,
                                                                        condition.unknownVars, pBCL))
                arrWithFunctionNames.append(condition.funcName)
                ranges = getRangesInClosedInterval([condition.ranges[0][0], condition.ranges[0][1],
                                                    self.gridStep[0]], 
                                                   [condition.ranges[1][0],
                                                    condition.ranges[1][1], self.gridStep[1]])
                sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
            # for saveDomain
            blockFunctionMap.update({sideName:sideLst}) 
        return ''.join(outputStr)
    
    def createVertexCondLst(self, totalBCondLst):
        '''
        DESCRIPTION:
        Создание списка условий на углы.
        В него входят условия с уже распарсенными значениями.

        From list of conditions at edges.

        
        INPUT:
        totalBCondLst - list of Connection or BoundCondition
                        objects, containing values property with
                        function strings for bounds.

        USED IN:
        generateBoundsAndIcs
        '''
        
        condCntOnS2 = len(totalBCondLst[0])
        condCntOnS3 = len(totalBCondLst[1])
        condCntOnS0 = len(totalBCondLst[2])
        condCntOnS1 = len(totalBCondLst[3])

        vertexCondList = [[totalBCondLst[0][0], totalBCondLst[2][0]],  # vertex (side_0, side_2)
                          [totalBCondLst[0][condCntOnS2-1], totalBCondLst[3][0]], # vertex (side_2, side_1)
                         [totalBCondLst[1][0], totalBCondLst[2][condCntOnS0-1]], # vertex (side_3, side_0)
                          [totalBCondLst[1][condCntOnS3-1],
                           totalBCondLst[3][condCntOnS1-1]]] # vertex (side_3, side_1)

        return vertexCondList
    
    def EquationLieOnSomeBound(self, condition):
        return condition.ranges[0][0] == condition.ranges[0][1] and condition.ranges[1][0] == condition.ranges[1][1]
    
    def SomeConditions(self, bRegion, stepFrom, stepTo, vmin, vmax):
        cond1 = stepFrom(bRegion) >= vmin and stepFrom(bRegion) <= vmax
        cond2 = stepTo(bRegion) > vmin and stepTo(bRegion) <= vmax and stepFrom(bRegion) < vmin
        cond3 = stepFrom(bRegion) < vmin and stepTo(bRegion) > vmax
        return [cond1, cond2, cond3]
    
    def generateVertexFunctions(self, blockNumber, arrWithFunctionNames, parsedVertexCondList):
        '''
        DESCRIPTION:
        Generate cpp string like:
        //Default boundary condition for Vertex between boundaries x = 0 and y = 0
        void Block1DefaultNeumannBoundForVertex0_2(double* result,
                                                   double** source,
                                                   double t, int idxX,
                                                   int idxY, int idxZ,
                                                   double* params, double** ic){

	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = source[0][idx];
        }

        USED FUNCTIONS:
        determineNameOfBoundary
        generateNeumannOrInterconnect
        generateDirichlet
        '''
        # parsedVertexCondList --- это список пар [[условие 1, условие 2], [условие 1, условие 2], ...]
        output = list()
        icsvCounter = 0
        for vertexCond in parsedVertexCondList:
            parsedEqs = vertexCond[0].parsedEquation
            unknownVars = vertexCond[0].unknownVars
            
            boundaryName1 = determineNameOfBoundary(vertexCond[0].side)
            boundaryName2 = determineNameOfBoundary(vertexCond[1].side)
            funcIndex = str(vertexCond[0].side) + '_' + str(vertexCond[1].side) + '__Eqn' + str(vertexCond[0].equationNumber)
            if not isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection):
                if vertexCond[0].boundNumber == vertexCond[1].boundNumber == -1:
                    output.append('//Default boundary condition for Vertex between boundaries '
                                  + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition for Vertex between boundaries '
                              + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if vertexCond[0].btype == vertexCond[1].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'Neumann__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                elif vertexCond[0].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
            elif isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection):
                if vertexCond[1].boundNumber == -1:
                    output.append('//Default boundary condition and interconnect for Vertex between boundaries '
                                  + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = ('Block' + str(blockNumber) +
                                     'DefaultNeumannAndInterconnect__Vertex' + funcIndex)
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition and interconnect for Vertex between boundaries '
                              + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if vertexCond[1].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
            elif not isinstance(vertexCond[0], Connection) and isinstance(vertexCond[1], Connection):
                if vertexCond[0].boundNumber == -1:
                    output.append('//Default boundary condition and interconnect for Vertex between boundaries '
                                  + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    nameForVertex = ('Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Vertex'
                                     + funcIndex)
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                    arrWithFunctionNames.append(nameForVertex)
                    continue
                output.append('//Non-default boundary condition and interconnect for Vertex between boundaries '
                              + boundaryName1 + ' and ' + boundaryName2 + '\n')
                if vertexCond[0].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                      parsedEqs, unknownVars, vertexCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'DirichletAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
            else:
                output.append('//Interconnect for Vertex between boundaries '
                              + boundaryName1 + ' and ' + boundaryName2 + '\n')
                nameForVertex = 'Block' + str(blockNumber) + 'Interconnect__Vertex' + funcIndex
                output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex,
                                                                  parsedEqs, unknownVars, vertexCond)])
                icsvCounter += 1
            
            arrWithFunctionNames.append(nameForVertex)
        return ''.join(output)
