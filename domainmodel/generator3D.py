# -*- coding: utf-8 -*-
'''
Created on 11 авг. 2015 г.

@author: golubenets
'''
from abstractGenerator import AbstractGenerator, BoundCondition, Connection, InterconnectRegion3D
from equationParser import MathExpressionParser
from someFuncs import determineNameOfBoundary, squareOrVolume, getRanges, splitBigRect, intersectionOfRects, getCellCountAlongLine

class Generator3D(AbstractGenerator):
    def __init__(self, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(Generator3D,self).__init__(haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(equations[block.defaultEquation].system))
            self.allBlockOffsetList.append([block.offsetX, block.offsetY, block.offsetZ])
            self.allBlockSizeList.append([block.sizeX, block.sizeY, block.sizeZ])
            self.__createBlockIcsRegions(block)
    
    def __createBlockIcsRegions(self, block):
        blockNumber = self.blocks.index(block)
        icsRegions = []
        firstIndex = 0
        for interconnect in self.interconnects:
            if interconnect.block1 == blockNumber and interconnect.block2 == blockNumber:
                icsRegions.append(self.__createIcRegion(blockNumber, interconnect.block2Side, block, self.blocks[interconnect.block1], firstIndex))
                firstIndex += 1
                icsRegions.append(self.__createIcRegion(blockNumber, interconnect.block1Side, block, self.blocks[interconnect.block2], firstIndex))
                firstIndex += 1
            elif interconnect.block1 == blockNumber and interconnect.block2 != blockNumber:
                icsRegions.append(self.__createIcRegion(blockNumber, interconnect.block1Side, block, self.blocks[interconnect.block2], firstIndex))
                firstIndex += 1
            elif interconnect.block2 == blockNumber and interconnect.block1 != blockNumber:
                icsRegions.append(self.__createIcRegion(blockNumber, interconnect.block2Side, block, self.blocks[interconnect.block1], firstIndex))
                firstIndex += 1
        block.interconnectRegions = icsRegions
                
    def __createIcRegion(self, mainBlockNum, mainBlockSide, mainBlock, secBlock, firstIndex):
        if mainBlockSide / 2 == 0:
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            zfrom = max([secBlock.offsetZ, mainBlock.offsetZ]) - mainBlock.offsetZ
            zto = min([mainBlock.offsetZ + mainBlock.sizeZ, secBlock.offsetZ + secBlock.sizeZ]) - mainBlock.offsetZ
            startCellIdx1Dir = getCellCountAlongLine(yfrom, self.gridStep[1])
            startCellIdx2Dir = getCellCountAlongLine(zfrom, self.gridStep[2])
            cellCountAlong1Dir = getCellCountAlongLine(yto - yfrom, self.gridStep[1])
            secondIndex = '((idxY + ' + str(cellCountAlong1Dir) + ' * idxZ) - '
            if mainBlockSide == 0:
                xfrom = 0
                xto = 0
            else:
                xfrom = mainBlock.sizeX
                xto = mainBlock.sizeX
        elif mainBlockSide / 2 == 1:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            zfrom = max([secBlock.offsetZ, mainBlock.offsetZ]) - mainBlock.offsetZ
            zto = min([mainBlock.offsetZ + mainBlock.sizeZ, secBlock.offsetZ + secBlock.sizeZ]) - mainBlock.offsetZ
            startCellIdx1Dir = getCellCountAlongLine(xfrom, self.gridStep[0])
            startCellIdx2Dir = getCellCountAlongLine(zfrom, self.gridStep[2])
            cellCountAlong1Dir = getCellCountAlongLine(xto - xfrom, self.gridStep[0])
            secondIndex = '((idxX + ' + str(cellCountAlong1Dir) + ' * idxZ) - '
            if mainBlockSide == 2:
                yfrom = 0
                yto = 0
            else:
                yfrom = mainBlock.sizeY
                yto = mainBlock.sizeY
        else:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            startCellIdx1Dir = getCellCountAlongLine(xfrom, self.gridStep[0])
            startCellIdx2Dir = getCellCountAlongLine(yfrom, self.gridStep[1])
            cellCountAlong1Dir = getCellCountAlongLine(xto - xfrom, self.gridStep[0])
            secondIndex = '((idxX + ' + str(cellCountAlong1Dir) + ' * idxY) - '
            if mainBlockSide == 4:
                zfrom = 0
                zto = 0
            else:
                zfrom = mainBlock.sizeZ
                zto = mainBlock.sizeZ
        secondIndex += '('+str(startCellIdx1Dir)+' + '+str(cellCountAlong1Dir)+' * '+str(startCellIdx2Dir)+')) * Block'+str(mainBlockNum)+'CELLSIZE'
        return InterconnectRegion3D(firstIndex, secondIndex, mainBlockSide, xfrom, xto, yfrom, yto, zfrom, zto, self.blocks.index(secBlock))
            
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
        edgesNames, vertexesNames = self.sideConfigs3(block, side)
        #В массиве allRectsOnSide будут содержаться словари вида {'ranges', 'eNum', 'e'}, каждый из которых соответствует какому-то
        #прямоугольнику на границе
        allRectsOnSide = self.determineSpaceOnTheBoundWithDefaultEquation(block, side)
        #Идем по всем прямоугольникам на границе и создаем для каждого из них одно или несколько краевых условий
        boundAndInterconnectRegions = block.boundRegions + block.interconnectRegions
        for rectMap in allRectsOnSide:
            dRect = rectMap['ranges']
            equationNum = rectMap['eNum']
            equation = rectMap['e']
            newDomainAfterSpliting = [dRect]
            for region in boundAndInterconnectRegions:
                #Находим очередное граничное условие на данную границу; это прямоугольник
                if region.side != side:
                    continue
                if side == 0 or side == 1:
                    rect = [region.yfrom, region.yto, region.zfrom, region.zto]
                elif side == 2 or side == 3:
                    rect = [region.xfrom, region.xto, region.zfrom, region.zto]
                else:
                    rect = [region.xfrom, region.xto, region.yfrom, region.yto]
                    
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
                    ranges = self.determine3DCoordinatesForBCond(block, side, intersection)
                    #Находим все ребра (и их координаты относительно ребра) и углы, которых касается прямоугольник
                    edges, vertexes = self.createVertexAndEdgeLsts(intersection, boundary, edgesNames, vertexesNames)
                    #Создаем либо соединение, либо граничное условие
                    if isinstance(region, InterconnectRegion3D):
                        funcName = "Block" + str(blockNumber) + "Interconnect__Side" + str(region.side) + "_Eqn" + str(equationNum) + "_SBlock" + str(region.secondaryBlockNumber)
                        condition = Connection(region.firstIndex, region.secondIndex, side, ranges, equationNum, equation, funcName)
                        condition.setSecondaryBlockIdx(region.secondaryBlockNumber)
                    else:
                        values, btype, boundNumber, funcName = self.setDirichletOrNeumann(region, blockNumber, side, equationNum)
                        condition = BoundCondition(values, btype, side, ranges, boundNumber, equationNum, equation, funcName)
                    #У него создаем поля с именами и координатами ребер и углов, которых касается прямоугольник
                    condition.setEdgesAndVertexesIn3D(edges, vertexes)
                    bCondList.append(condition)
                    #Находим кусок области, не затронутый граничным условием (соединением)
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
                values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)
                for domain in newDomainAfterSpliting:
                    edges, vertexes = self.createVertexAndEdgeLsts(domain, boundary, edgesNames, vertexesNames)
                    ranges = self.determine3DCoordinatesForBCond(block, side, domain)
                    defCondition = BoundCondition(values, btype, side, ranges, boundNumber, equationNum, equation, funcName)
                    defCondition.setEdgesAndVertexesIn3D(edges, vertexes)
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
            edgesNames = ['02', '03', '04', '05']
            vertexesNames = ['024', '034', '025', '035']
        elif side == 1:
            edgesNames = ['12', '13', '14', '15']
            vertexesNames = ['124', '134', '125', '135']
        elif side == 2:
            edgesNames = ['02', '12', '24', '25']
            vertexesNames = ['024', '124', '025', '125']
        elif side == 3:
            edgesNames = ['03', '13', '34', '35']
            vertexesNames = ['034', '134', '035', '135']
        elif side == 4:
            edgesNames = ['04', '14', '24', '34']
            vertexesNames = ['024', '124', '034', '134']
        else:
            edgesNames = ['05', '15', '25', '35']
            vertexesNames = ['025', '125', '035', '135']
        return edgesNames, vertexesNames
    
    def createVertexAndEdgeLsts(self, rect, boundary, edgesNames, vertexesNames):
        #Составляет списки ребер и углов, которых касается граничное условие
        #Ребра будут возвращаться в формате списка с элементами вида {"название": [xfrom, xto]} (т.е. координаты относительно ребра!!!)
        edges = {}
        vertexes = []
        if rect[0] == boundary[0]:
            edges.update({edgesNames[0]: [rect[2], rect[3]]})
            if rect[2] == boundary[2]:
                vertexes.append(vertexesNames[0])
                edges.update({edgesNames[2]: [rect[0], rect[1]]})
            if rect[3] == boundary[3]:
                vertexes.append(vertexesNames[2])
                edges.update({edgesNames[3]: [rect[0], rect[1]]})
        if rect[2] == boundary[2]:
            if edgesNames[2] not in edges:
                edges.update({edgesNames[2]: [rect[0], rect[1]]})
            if rect[1] == boundary[1]:
                vertexes.append(vertexesNames[1])
                edges.update({edgesNames[1]: [rect[2], rect[3]]})
        if rect[1] == boundary[1]:
            if edgesNames[1] not in edges:
                edges.update({edgesNames[1]: [rect[2], rect[3]]})
            if rect[3] == boundary[3]:
                vertexes.append(vertexesNames[3])
                if edgesNames[3] not in edges:
                    edges.update({edgesNames[3]: [rect[0], rect[1]]})
        if rect[3] == boundary[3]:
            if edgesNames[3] not in edges:
                edges.update({edgesNames[3]: [rect[0], rect[1]]})
        return edges, vertexes

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
        blockFunctionMap.update({"v024":bfmLen - 8, "v124":bfmLen - 7, "v034":bfmLen - 6, "v134":bfmLen - 5, "v025":bfmLen - 4, "v125":bfmLen - 3, "v035":bfmLen - 2, "v135":bfmLen - 1 })
        #Создаем список условий на ребра, генерируем функции на ребра и добавляем всю инфу в blockFunctionMap
        parsedEdgeCondList = self.createEdgeCondLst(totalBCondLst)
        #После работы этой функции словарь parsedEdgeCondList изменится и будет для каждого ребра содержать
        #список с его условиями. Этот список готов для занесения без изсенений в blockFunctionMap
        outputStr.append(self.generateEdgesFunctions(block, blockNumber, arrWithFunctionNames, parsedEdgeCondList))
        for edge in parsedEdgeCondList:
            blockFunctionMap.update({"edge" + edge: parsedEdgeCondList[edge]})
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
        for vertexCond in parsedVertexCondList:
            parsedEqs = vertexCond[0].parsedEquation
            unknownVars = vertexCond[0].unknownVars
            
            bName1 = determineNameOfBoundary(vertexCond[0].side)
            bName2 = determineNameOfBoundary(vertexCond[1].side)
            bName3 = determineNameOfBoundary(vertexCond[2].side)
            funcIndex = str(vertexCond[0].side) + '_' + str(vertexCond[1].side) + '_' + str(vertexCond[2].side) + '__Eqn' + str(vertexCond[0].equationNumber)
            #Ни на одной из трех границ нет соединения, затрагивающего угол
            if not isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection) and not isinstance(vertexCond[2], Connection):
#                 if vertexCond[0].boundNumber == vertexCond[1].boundNumber == vertexCond[2].boundNumber == -1:
#                     output.append('//Default boundary condition for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumann__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
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
            #На одной из трех границ есть соединение, затрагивающее угол. Вариант 1
            elif isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection) and not isinstance(vertexCond[2], Connection):
#                 if vertexCond[1].boundNumber == vertexCond[2].boundNumber == -1:
#                     output.append('//Two default boundary conditions and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'TwiceDefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
#                 elif vertexCond[1].boundNumber == -1 and vertexCond[2].btype == 1 or vertexCond[1].btype == 1 and vertexCond[2].boundNumber == -1:
#                     output.append('//Default boundary condition, nondefault boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndNondefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[1].btype == 1 and vertexCond[2].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                elif vertexCond[1].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[2])])
            #На одной из трех границ есть соединение, затрагивающее угол. Вариант 2        
            elif not isinstance(vertexCond[0], Connection) and isinstance(vertexCond[1], Connection) and not isinstance(vertexCond[2], Connection):
#                 if vertexCond[0].boundNumber == vertexCond[2].boundNumber == -1:
#                     output.append('//Two default boundary conditions and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'TwiceDefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
#                 elif vertexCond[0].boundNumber == -1 and vertexCond[2].boundNumber == 1 or vertexCond[0].boundNumber == 1 and vertexCond[2].boundNumber == -1:
#                     output.append('//Default boundary condition, nondefault boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndNondefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[0].btype == 1 and vertexCond[2].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                elif vertexCond[0].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[2])])
            #На одной из трех границ есть соединение, затрагивающее угол. Вариант 3        
            elif not isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection) and isinstance(vertexCond[2], Connection):
#                 if vertexCond[1].boundNumber == vertexCond[0].boundNumber == -1:
#                     output.append('//Two default boundary conditions and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'TwiceDefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
#                 elif vertexCond[1].boundNumber == -1 and vertexCond[0].boundNumber == 1 or vertexCond[1].boundNumber == 1 and vertexCond[0].boundNumber == -1:
#                     output.append('//Default boundary condition, nondefault boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndNondefaultNeumannAndInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[1].btype == 1 and vertexCond[0].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                elif vertexCond[1].btype == 0:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
            #На двух из трех границ есть соединения, затрагивающие угол. Вариант 1
            elif isinstance(vertexCond[0], Connection) and isinstance(vertexCond[1], Connection) and not isinstance(vertexCond[2], Connection):
#                 if vertexCond[2].boundNumber == -1:
#                     output.append('//Default boundary condition and twice interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndTwiceInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and double interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[2].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndDoubleInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[2])])
            #На двух из трех границ есть соединения, затрагивающие угол. Вариант 2        
            elif isinstance(vertexCond[0], Connection) and not isinstance(vertexCond[1], Connection) and isinstance(vertexCond[2], Connection):
#                 if vertexCond[1].boundNumber == -1:
#                     output.append('//Default boundary condition and twice interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndTwiceInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and double interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[1].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndDoubleInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[1])])
            #На двух из трех границ есть соединения, затрагивающие угол. Вариант 3
            elif not isinstance(vertexCond[0], Connection) and isinstance(vertexCond[1], Connection) and isinstance(vertexCond[2], Connection):
#                 if vertexCond[0].boundNumber == -1:
#                     output.append('//Default boundary condition and twice interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
#                     nameForVertex = 'Block' + str(blockNumber) + 'DefaultNeumannAndTwiceInterconnect__Vertex' + funcIndex
#                     output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
#                     arrWithFunctionNames.append(nameForVertex)
#                     continue
                output.append('//Boundary condition and double interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                if vertexCond[0].btype == 1:
                    nameForVertex = 'Block' + str(blockNumber) + 'NeumannAndDoubleInterconnect__Vertex' + funcIndex
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
                else:
                    nameForVertex = 'Block' + str(blockNumber) + 'Dirichlet__Vertex' + funcIndex
                    output.extend([self.generateDirichlet(blockNumber, nameForVertex, vertexCond[0])])
            #На всех трех границах есть соединения, затрагивающие угол
            else:
                output.append('//Interconnect for Vertex between boundaries ' + bName1 + ', ' + bName2 + ' and ' + bName3 + '\n')
                nameForVertex = 'Block' + str(blockNumber) + 'Interconnect__Vertex' + funcIndex
                output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForVertex, parsedEqs, unknownVars, vertexCond)])
            
            arrWithFunctionNames.append(nameForVertex)
        return ''.join(output)

    def createEdgeCondLst(self, totalBCondLst):
        #Формирует всевозможные условия на ребра (пары граничных условий) вместе с одномерными координатами (относительно ребра)
        #области, на которой каждое условие задано
        #В эту функцию передаются условия с уже распарсенными значениями
        blockEdges = {'04': [], '05': [], '14': [], '15': [], '02': [], '03': [], '12': [], '13': [], '24': [], '25': [], '34': [], '35': []}
        #Этот словарь задает соответствие вида {'сторона': индекс массива граничных условий в массиве totalBCondLst}
        correspondenceBetweenIndicesAndSides = {'4': 0, '5': 1, '2': 2, '3': 3, '0': 4, '1': 5}
        for edge in blockEdges:
            fSide = edge[0]
            sSide = edge[1]
            fIdx = correspondenceBetweenIndicesAndSides[fSide]
            sIdx = correspondenceBetweenIndicesAndSides[sSide]
            conditionsOnFirstSide = []
            conditionsOnSecondSide = []
            for bCond in totalBCondLst[fIdx]:
                if edge in bCond.edges:
                    conditionsOnFirstSide.append(bCond)
            for bCond in totalBCondLst[sIdx]:
                if edge in bCond.edges:
                    conditionsOnSecondSide.append(bCond)
            blockEdges[edge] = self.determineAllPairsOfConditionsForEdge(conditionsOnFirstSide, conditionsOnSecondSide, edge)
        return blockEdges
    
    def determineAllPairsOfConditionsForEdge(self, conditionsOnFirstSide, conditionsOnSecondSide, edge):
        #Функция создает условие на ребро (= пара граничных условий) + одномерные координаты места, на котором оно задано
        allPairs = []
        for condition1 in conditionsOnFirstSide:
            for condition2 in conditionsOnSecondSide:
                segment1 = condition1.edges[edge]
                segment2 = condition2.edges[edge]
                intersection = self.segmentsIntersects(segment1, segment2)
                if len(intersection) == 0:
                    continue
                allPairs.append((condition1, condition2, intersection))   
        return allPairs
    
    def generateEdgesFunctions(self, block, blockNumber, arrWithFunctionNames, parsedEdgeCondList):
        #Генерирует все функции для всех ребер, создает словарь типа blockFunctionMap, где для каждого ребра указан список,
        #состоящий из списков вида [№ функции, границы]
        output = list()
        for edge in parsedEdgeCondList:
            boundAndEquatNumberList = []
            listOfConditionsForEdge = []
            for edgeCond in parsedEdgeCondList[edge]:
                parsedEqs = edgeCond[0].parsedEquation
                unknownVars = edgeCond[0].unknownVars
                ranges1D = edgeCond[2]
                ranges3D = self.determine3DCoordinatesForCondOnEdge(block, ranges1D, edge)
                ranges = getRanges([ranges3D[0], ranges3D[1], self.gridStep[0], block.sizeX], [ranges3D[2], ranges3D[3], self.gridStep[1], block.sizeY], [ranges3D[4], ranges3D[5], self.gridStep[2], block.sizeZ])
                
                boundaryName1 = determineNameOfBoundary(edgeCond[0].side)
                boundaryName2 = determineNameOfBoundary(edgeCond[1].side)
                fBCond = self.createSomeName(edgeCond[0])
                sBCond = self.createSomeName(edgeCond[1])
                funcIndex = str(edgeCond[0].side) + '_' + str(edgeCond[1].side) + '__Eqn' + str(edgeCond[0].equationNumber) + '__FBCond' + fBCond + '__SBCond' + sBCond
                #Ни на одной из двух границ нет соединений, касающихся ребра
                if not isinstance(edgeCond[0], Connection) and not isinstance(edgeCond[1], Connection):
#                     if edgeCond[0].boundNumber == edgeCond[1].boundNumber == -1:
#                         nameForEdge = 'Block' + str(blockNumber) + 'DefaultNeumann__Edge' + funcIndex
#                         if (edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
#                             listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                             continue
#                         boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
#                         output.append('//Default boundary condition for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
#                         arrWithFunctionNames.append(nameForEdge)
#                         listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                         continue
                    output.append('//Boundary condition for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    if edgeCond[0].btype == edgeCond[1].btype == 1:
                        nameForEdge = 'Block' + str(blockNumber) + 'Neumann__Edge' + funcIndex
                        if (edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
                        output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
                    elif edgeCond[0].btype == 0:
                        nameForEdge = 'Block' + str(blockNumber) + 'Dirichlet__Edge' + funcIndex
                        if (edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForEdge, edgeCond[0])])
                    else:
                        nameForEdge = 'Block' + str(blockNumber) + 'Dirichlet__Edge' + funcIndex
                        if (edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForEdge, edgeCond[1])])
                #На одной из двух границ есть соединения, касающиеся ребра. Вариант 1        
                elif isinstance(edgeCond[0], Connection) and not isinstance(edgeCond[1], Connection):
#                     if edgeCond[1].boundNumber == -1:
#                         nameForEdge = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Edge' + funcIndex
#                         if (edgeCond[0].secondaryBlockIdx, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
#                             listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                             continue
#                         boundAndEquatNumberList.append((edgeCond[0].secondaryBlockIdx, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
#                         output.append('//Default boundary condition and interconnect for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
#                         arrWithFunctionNames.append(nameForEdge)
#                         listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                         continue
                    output.append('//Boundary condition and interconnect for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    if edgeCond[1].btype == 1:
                        nameForEdge = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Edge' + funcIndex
                        if (edgeCond[0].secondaryBlockIdx, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].secondaryBlockIdx, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
                        output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
                    else:
                        nameForEdge = 'Block' + str(blockNumber) + 'Dirichlet__Edge' + funcIndex
                        if (edgeCond[0].secondaryBlockIdx, edgeCond[1].boundNumber, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((-1, edgeCond[1].boundNumber, edgeCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForEdge, edgeCond[1])])
                #На одной из двух границ есть соединения, касающиеся ребра. Вариант 2        
                elif not isinstance(edgeCond[0], Connection) and isinstance(edgeCond[1], Connection):
#                     if edgeCond[0].boundNumber == -1:
#                         nameForEdge = 'Block' + str(blockNumber) + 'DefaultNeumannAndInterconnect__Edge' + funcIndex
#                         if (edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber) in boundAndEquatNumberList:
#                             listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                             continue
#                         boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber))
#                         output.append('//Default boundary condition and interconnect for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
#                         output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
#                         arrWithFunctionNames.append(nameForEdge)
#                         listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
#                         continue
                    output.append('//Boundary condition and interconnect for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    if edgeCond[0].btype == 1:
                        nameForEdge = 'Block' + str(blockNumber) + 'NeumannAndInterconnect__Edge' + funcIndex
                        if (edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber))
                        output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
                    else:
                        nameForEdge = 'Block' + str(blockNumber) + 'Dirichlet__Edge' + funcIndex
                        if (edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                            listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                            continue
                        boundAndEquatNumberList.append((edgeCond[0].boundNumber, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber))
                        output.extend([self.generateDirichlet(blockNumber, nameForEdge, edgeCond[0])])
                #На обеих границах есть соединения, касающиеся ребра
                else:
                    nameForEdge = 'Block' + str(blockNumber) + 'Interconnect__Edge' + funcIndex
                    if (edgeCond[0].secondaryBlockIdx, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber) in boundAndEquatNumberList:
                        listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
                        continue
                    boundAndEquatNumberList.append((edgeCond[0].secondaryBlockIdx, edgeCond[1].secondaryBlockIdx, edgeCond[0].equationNumber))
                    output.append('//Interconnect for Edge between boundaries ' + boundaryName1 + ' and ' + boundaryName2 + '\n')
                    output.extend([self.generateNeumannOrInterconnect(blockNumber, nameForEdge, parsedEqs, unknownVars, [edgeCond[0], edgeCond[1]])])
                
                arrWithFunctionNames.append(nameForEdge)
                listOfConditionsForEdge.append([arrWithFunctionNames.index(nameForEdge)] + ranges)
            parsedEdgeCondList[edge] = listOfConditionsForEdge
        return ''.join(output)
    
    def createSomeName(self, condition):
        if isinstance(condition, Connection):
            return 'Block' + str(condition.secondaryBlockIdx)
        if condition.boundNumber == -1:
            return 'Def'
        else:
            return str(condition.boundNumber)
    
    def determine3DCoordinatesForCondOnEdge(self, block, condRangesOnEdge, edge):
        if edge == '04':
            return [0, 0, condRangesOnEdge[0], condRangesOnEdge[1], 0, 0]
        elif edge == '05':
            return [0, 0, condRangesOnEdge[0], condRangesOnEdge[1], block.sizeZ, block.sizeZ]
        elif edge == '14':
            return [block.sizeX, block.sizeX, condRangesOnEdge[0], condRangesOnEdge[1], 0, 0]
        elif edge == '15':
            return [block.sizeX, block.sizeX, condRangesOnEdge[0], condRangesOnEdge[1], block.sizeZ, block.sizeZ]
        elif edge == '02':
            return [0, 0, 0, 0, condRangesOnEdge[0], condRangesOnEdge[1]]
        elif edge == '03':
            return [0, 0, block.sizeY, block.sizeY, condRangesOnEdge[0], condRangesOnEdge[1]]
        elif edge == '12':
            return [block.sizeX, block.sizeX, 0, 0, condRangesOnEdge[0], condRangesOnEdge[1]]
        elif edge == '13':
            return [block.sizeX, block.sizeX, block.sizeY, block.sizeY, condRangesOnEdge[0], condRangesOnEdge[1]]
        elif edge == '24':
            return [condRangesOnEdge[0], condRangesOnEdge[1], 0, 0, 0, 0]
        elif edge == '34':
            return [condRangesOnEdge[0], condRangesOnEdge[1], block.sizeY, block.sizeY, 0, 0]
        elif edge == '25':
            return [condRangesOnEdge[0], condRangesOnEdge[1], 0, 0, block.sizeZ, block.sizeZ]
        elif edge == '35':
            return [condRangesOnEdge[0], condRangesOnEdge[1], block.sizeY, block.sizeY, block.sizeZ, block.sizeZ]
     
    def segmentsIntersects(self, segment1, segment2):
        intersection = [max([segment1[0], segment2[0]]), min([segment1[1], segment2[1]])]
        if intersection[0] >= intersection[1]:
            return []
        else:
            return intersection