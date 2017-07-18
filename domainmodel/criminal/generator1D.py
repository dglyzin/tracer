# -*- coding: utf-8 -*-
'''
Created on 11 авг. 2015 г.

@author: golubenets
'''
from abstractGenerator import AbstractGenerator, BoundCondition, Connection
from ..equationParser import MathExpressionParser
from someFuncs import determineNameOfBoundary, getRangesInClosedInterval


class Generator1D(AbstractGenerator):
    def __init__(self, model):

        AbstractGenerator.__init__(self, model)

        self.cellsizeList = list()
        self.allBlockSizeList = list()
        self.allBlockOffsetList = list()
        equations = model.equations

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

        OUTPUT:
        Function like:
        void Block0FillInitialValues(double*...){
        ...
        }

        USED FUNCTIONS:
        self.genCommonPartForFillInitValFunc
        self.blocks
        
        '''
        lWIFN = listWithInitialFunctionNames
        lWDFN = listWithDirichletFunctionNames

        totalCountOfInitials = len(lWIFN)
        allFillFunctions = list()
        for blockNumber, block in enumerate(self.blocks):
            strBlockNum = str(blockNumber)
            fillFunction = self.genCommonPartForFillInitValFunc(block, blockNumber,
                                                                totalCountOfInitials, lWIFN, lWDFN)
            fillFunction += "\tfor(int idxX = 0; idxX<Block" + strBlockNum + "CountX; idxX++){\n"
            fillFunction += "\t\tint idx = idxX;\n" #*Block" + strBlockNum + "CELLSIZE
            fillFunction += "\t\tint type = initType[idx];\n"
            fillFunction += ("\t\tinitFuncArray[type](result+idx*Block" + strBlockNum
                             + "CELLSIZE, Block" + strBlockNum + "OffsetX + idxX*DX, 0, 0);\n\t}\n")
            fillFunction += "}\n\n"
            allFillFunctions.append(fillFunction)
        return ''.join(allFillFunctions)
    
    def createListOfBCondsForSide(self, block, blockNumber, side):
        '''
        DESCRIPTION:
        Using block.BoundRegions and block.equationRegions to
        create BoundCondition objects list for each side.

        OUTPUT:
        BoundCondition object

        USED FUNCTIONS:
        block.equationRegions
        block.equationNumber

        self.equations

        self.setDirichletOrNeumann
        self.setDefault

        USED IN:
        getBlockInfo
        '''
        # for equation regions
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

        # for bound regions
        for bRegion in block.boundRegions:
            if bRegion.side == side:
                # if exist special region for that side
                values, btype, boundNumber, funcName = self.setDirichletOrNeumann(bRegion, blockNumber,
                                                                                  side, equationNum)
                break
        else:
            # if not, use default
            values, btype, boundNumber, funcName = self.setDefault(blockNumber, side, equation, equationNum)

        return BoundCondition(values, btype, side, [], boundNumber,
                              equationNum, equation, funcName,
                              block, blockNumber = blockNumber)
    
    def createListOfInterconnects(self, block, blockNumber):
        '''
        OUTPUT:
        List of Connection objects.

        USED FUNCTIONS:
        block.equationRegions
        block.defaultEquation

        self.equations

        USED IN:
        getBlockInfo
        '''
        icsForBlock = []
        for iconn in self.interconnects:
            #Если блок зациклен.
            if iconn.block1 == blockNumber and iconn.block2 == blockNumber:

                # choice left or right side of block
                # i.e. 0.0 or block.sizeX
                Range1 = (iconn.block1Side == 1) * block.sizeX
                Range2 = (iconn.block2Side == 1) * block.sizeX

                # return either xfrom or xto for block
                coord1 = lambda region: ((iconn.block1Side == 0) * region.xfrom
                                         + (iconn.block1Side == 1) * region.xto)
                coord2 = lambda region: ((iconn.block2Side == 0) * region.xfrom
                                         + (iconn.block2Side == 1) * region.xto)

                # for first block
                for eqRegion in block.equationRegions:
                    # for ex:
                    # region.xfrom == 0.0
                    # or region.xto == block.sizeX
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
                funcName1 = ("Block" + str(blockNumber) + "Interconnect__Side"
                             + str(iconn.block1Side) + "_Eqn" + str(equationNum1))
                funcName2 = ("Block" + str(blockNumber) + "Interconnect__Side"
                             + str(iconn.block2Side) + "_Eqn" + str(equationNum2))
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

            # for default
            firstIndex = len(icsForBlock)
            Range = (side == 1) * block.sizeX
            coord = lambda region: (side == 0) * region.xfrom + (side == 1) * region.xto

            for eqRegion in block.equationRegions:
                if coord(eqRegion) == Range:
                    equationNum = eqRegion.equationNumber
                    break
            else:
                equationNum = block.defaultEquation
            equation = self.equations[equationNum]

            funcName = ("Block" + str(blockNumber) + "Interconnect__Side"
                        + str(side) + "_Eqn" + str(equationNum))
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
            # for check if condition is interconnect
            # i.e. contained in icsList
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
 
        # for blockFunctionMap
        sideName = "side"+str(condition.side)

        outputStr = '//Boundary condition for boundary ' + boundaryName + '\n'
        if condition.btype == 0:
            outputStr += self.generateDirichlet(blockNumber, condition.funcName, condition)
        else:
            pBCL = [condition]
            outputStr += self.generateNeumannOrInterconnect(blockNumber, condition.funcName, condition.parsedEquation, condition.unknownVars, pBCL)

        # for setDomain
        idx = len(arrWithFunctionNames)
        blockFunctionMap.update({sideName: idx})

        # for init
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


class BlockInfo():
    def __init__(self):
        # self.block = block

        self.systemsForCentralFuncs = None
        self.numsForSystems = None
        self.totalBCondLst = None
        self.totalInterconnectLst = None
        self.blockFuncMap = None

        # for debugging:
        self.dbg = True
        self.dbgInx = 3
    
    def getBlockInfo(self, gen, block, blockNumber):
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
        createListOfInterconnects

        self.equations
        
        USED IN:
        FuncGenerator.generateAllFunctions
        
        '''
        # for debug
        self.print_dbg("FROM getBlockInfo:")

        systemsForCentralFuncs = []
        numsForSystems = []
        blockFuncMap = {'center': []}
        reservedSpace = 0

        # split equations at regions
        for eqRegion in block.equationRegions:
            reservedSpace += eqRegion.xto - eqRegion.xfrom
            
            # for removing trivial cases
            cond = (eqRegion.xfrom == eqRegion.xto
                    and
                    (eqRegion.xto == 0.0 or eqRegion.xto == block.sizeX))

            if eqRegion.equationNumber not in numsForSystems and not cond:
                systemsForCentralFuncs.append(gen.equations[eqRegion.equationNumber])
                numsForSystems.append(eqRegion.equationNumber)
            if not cond:

                # Каждую функцию характеризует не длина в координатах,
                # а диапазон клеток, которые эта функция должна пересчитывать
                ranges = getRangesInClosedInterval([eqRegion.xfrom, eqRegion.xto, gen.gridStep[0]])
                blockFuncMap['center'].append([numsForSystems.index(eqRegion.equationNumber)] + ranges)

        # add default equation at remaining regions.
        if block.sizeX > reservedSpace:
            systemsForCentralFuncs.append(gen.equations[block.defaultEquation])
            blockFuncMap.update({'center_default': len(numsForSystems)})
            numsForSystems.append(block.defaultEquation)
        
        totalBCondLst = list()
        sides = [0, 1]
        for side in sides:
            totalBCondLst.append(gen.createListOfBCondsForSide(block, blockNumber, side))
            
        totalInterconnectLst = gen.createListOfInterconnects(block, blockNumber)

        # OUTPUT:
        self.systemsForCentralFuncs = systemsForCentralFuncs
        self.numsForSystems = numsForSystems
        self.totalBCondLst = totalBCondLst
        self.totalInterconnectLst = totalInterconnectLst
        self.blockFuncMap = blockFuncMap

        # for debug
        self.print_dbg("systemsForCentralFuncs:",
                       self.systemsForCentralFuncs)
        self.print_dbg("numsForSystems",
                       self.numsForSystems)
        self.print_dbg("totalBCondLst",
                       self.totalBCondLst)
        self.print_dbg("totalInterconnectLst:",
                       self.totalInterconnectLst)
        self.print_dbg("blockFuncMap:",
                       self.blockFuncMap)

    def getPropertiesDict(self):
        return(self.__dict__)
    
    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')
