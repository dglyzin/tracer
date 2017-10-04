# -*- coding: utf-8 -*-
'''
Created on 11 авг. 2015 г.

@author: golubenets
'''
import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.abstractGenerator import AbstractGenerator, BoundCondition, Connection
    from domainmodel.equationParser import MathExpressionParser
    from domainmodel.someFuncs import determineNameOfBoundary, getRangesInClosedInterval

else:
    from abstractGenerator import AbstractGenerator, BoundCondition, Connection
    from ..equationParser import MathExpressionParser
    from someFuncs import determineNameOfBoundary, getRangesInClosedInterval


class Generator1D(AbstractGenerator):
    def __init__(self, delay_lst, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex):
        super(Generator1D,self).__init__(delay_lst, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        
        for block in self.blocks:
            self.cellsizeList.append(len(equations[block.defaultEquation].system))
            self.allBlockOffsetList.append([block.offsetX, 0, 0])
            self.allBlockSizeList.append([block.sizeX, 0, 0])
       
    def generateFillInitValFuncsForAllBlocks(self,
                                             listWithInitialFunctionNames,
                                             listWithDirichletFunctionNames):
        '''
        DESCRIPTION:
        Для каждого блока создает функцию-заполнитель с именем
        BlockIFillInitialValues (I-номер блока).
        '''
        totalCountOfInitials = len(listWithInitialFunctionNames)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
            strBlockNum = str(blockNumber)
            fillFunction = self.genCommonPartForFillInitValFunc(block, blockNumber,
                                                                totalCountOfInitials,
                                                                listWithInitialFunctionNames,
                                                                listWithDirichletFunctionNames)
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
                ranges = getRangesInClosedInterval([eqRegion.xfrom, eqRegion.xto, self.gridStep[0]])
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
        return BoundCondition(values, btype, side, [], boundNumber,
                              equationNum, equation, funcName,
                              block, blockNumber = blockNumber)
    
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
        
        condition.createSpecialProperties(parser, self.params, self.paramValues,
                                          indepVarsForBoundaryFunction)
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
