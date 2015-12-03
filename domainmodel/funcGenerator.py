# -*- coding: utf-8 -*-
from generator1D import Generator1D
from generator2D import Generator2D
from generator3D import Generator3D

class FuncGenerator:
    def __init__(self, maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex, preprocessorFolder):
        dimension = len(equations[0].vars) #number of independent variables
        if dimension == 1:
            self.generator = Generator1D(maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        elif dimension == 2:
            self.generator = Generator2D(maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
        else:
            self.generator = Generator3D(maxDerivOrder, haloSize, equations, blocks, initials, bounds, interconnects, gridStep, params, paramValues, defaultParamIndex)
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