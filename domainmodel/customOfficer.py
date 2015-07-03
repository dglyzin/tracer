# -*- coding: utf-8 -*-
'''
Created on 02 июля 2015 г.

@author: golubenets
'''
class Reviewer:
    def __init__(self, equations, blocks, initials, bounds, gridStep, params, paramValues, defaultParamsIndex):
        self.equations = equations
        self.blocks = blocks
        self.initials = initials
        self.bounds = bounds
        self.gridStep = gridStep
        self.params = params
        self.paramValues = paramValues
        self.defaultParamsIndex = defaultParamsIndex
    
    def ReviewInput(self):
        self.ReviewParameters()
        self.ReviewBlocks()
        
    def ReviewParameters(self):
        paramsCount = len(self.params)
        nonrequrringParamsCnt = len(set(self.params))
        if paramsCount != nonrequrringParamsCnt:
            raise AttributeError("INPUT_ERROR: Some parameter occurs more than once in list of parameters!")
        for idx, value in enumerate(self.paramValues):
            if len(value) != paramsCount:
                raise AttributeError("INPUT_ERROR: Count of parameter values in dictionary with index "+str(idx)+" doesn't correspond to count of parameters!")
            for parameter in value:
                if parameter not in self.params:
                    raise AttributeError("INPUT_ERROR: Parameter '"+parameter+"' is absent in list of parameters, but it is in dictionary with index "+str(idx)+" in list of parameter values!")
        parValLen = len(self.paramValues)
        if self.defaultParamsIndex >= parValLen or (parValLen > 0 and self.defaultParamsIndex < 0):
            raise AttributeError("INPUT_ERROR: DefaultParamsIndex has incorrect value!")
                
    def ReviewBlocks(self):
# Проверяет каждый блок.
        dimensionsSet = set()
        eqCnt = len(self.equations)
        initCnt = len(self.initials)
        for num, block in enumerate(self.blocks):
            if block.sizeX < 0 or block.dimension > 1 and block.sizeY < 0 or block.dimension > 2 and block.sizeZ < 0:
                raise AttributeError("INPUT_ERROR: Block size should be a positive real number for all directions!")
            if block.defaultEquation < 0 or block.defaultEquation >= eqCnt:
                raise AttributeError("INPUT_ERROR: Default equation index is incorrect for block with number "+str(num)+"!")
            if block.defaultInitial < 0 or block.defaultInitial >= initCnt:
                raise AttributeError("INPUT_ERROR: Default initial index is incorrect for block with number "+str(num)+"!")
            dimensionsSet.add(block.dimension)
        if len(dimensionsSet) > 1:
            raise AttributeError("INPUT_ERROR: All blocks should be of the same dimension!")
        equationIdxLst = [block.defaultEquation] + self.ReviewEqRegOrInitRegOrBoundReg(block, num, lambda block: block.equationRegions, lambda eqRegion: eqRegion.equationNumber, eqCnt, "Equation")
        systemsLen = self.ReviewEquations(equationIdxLst)
        initialIdxLst = [block.defaultInitial] + self.ReviewEqRegOrInitRegOrBoundReg(block, num, lambda block: block.initialRegions, lambda iRegion: iRegion.initialNumber, initCnt, "Initial")
        self.ReviewInitials(systemsLen, initialIdxLst)
        boundIdxLst = self.ReviewEqRegOrInitRegOrBoundReg(block, num, lambda block: block.boundRegions, lambda bRegion: bRegion.boundNumber, len(self.bounds), "Bound")
        self.ReviewBounds(systemsLen, boundIdxLst)

    def ReviewEqRegOrInitRegOrBoundReg(self, block, blockNum, Regions, Number, originalCnt, string):
# Проверяет корректность ввода регионов уравнений или регионов начальных условий для блока.
# originalCnt это количество уравнений в массиве block.equations (начальных условий в массиве block.initials),
# Regions это лямбда функция, берущая у блока equationRegions (initialRegions)
# Number это лямбда-функция, берущая у региона значение поля equationNumber (initialNumber, boundNumber)
        dim = block.dimension
        indexList = []
        for regNum, region in enumerate(Regions(block)):
            if Number(region) < 0 or Number(region) >= originalCnt:
                raise AttributeError("INPUT_ERROR: "+string+" number is incorrect in "+string+" Region "+str(regNum)+" for block with number "+str(blockNum)+"!")
            if region.xfrom > region.xto or dim > 1 and region.yfrom > region.yto or dim > 2 and region.zfrom > region.zto:
                raise AttributeError("INPUT_ERROR: The value for 'from' greater than the value for 'to' in "+string+" Region "+str(regNum)+" for block with number "+str(blockNum)+"!")
            cond1 = region.xfrom < 0 or dim > 1 and region.yfrom < 0 or dim > 2 and region.zfrom < 0
            cond2 = region.xto > block.sizeX or dim > 1 and region.yto > block.sizeY or dim > 2 and region.zto > block.sizeZ
            if cond1 or cond2:
                raise AttributeError("INPUT_ERROR: Coordinates for "+string+" Region "+str(regNum)+" for block with number "+str(blockNum)+" are incorrect! Part of the Region is outside the block!")
            if string == "Bound":
                if region.side < 0 or dim == 1 and region.side > 1 or dim == 2 and region.side > 3 or dim == 3 and region.side > 5:
                    raise AttributeError("INPUT_ERROR: Side is incorrect in Bound Region "+str(regNum)+" for block with number "+str(blockNum)+"!")
            indexList.append(Number(region))
        return indexList
            
    def ReviewEquations(self, equationIndexList):
# Проверяет только уравнения, участвующие в задаче!
        # Элемент множества -- количество уравнений в системе. Если множество будет содержать больше 1 элемента, то ошибка
        systemLenSet = set()
        varsSet = set()
        for idx in equationIndexList:
            systemLenSet.add(len(self.equations[idx].system))
            varsSet.add(tuple(self.equations[idx].vars))
        if len(systemLenSet) > 1:
            raise AttributeError("INPUT_ERROR: Systems of the problem has different count of equations!")
        if len(varsSet) > 1:
            raise AttributeError("INPUT_ERROR: Systems of the problem uses different independent variables sets!")
        return systemLenSet.pop()
    
    def ReviewInitials(self, systemsLen, initialIdxLst):
        for idx in initialIdxLst:
            l = len(self.initials[idx].values)
            if l != systemsLen:
                raise AttributeError("INPUT_ERROR: Initial condition with index "+str(idx)+" contain "+str(l)+" value components instead "+str(systemsLen)+"!")
    
    def ReviewBounds(self, systemsLen, boundIdxLst):
        for idx in boundIdxLst:
            if self.bounds[idx].btype == 1:
                l = len(self.bounds[idx].values)
            else:
                l1 = len(self.bounds[idx].values)
                l2 = len(self.bounds[idx].derivative)
                if l1 != l2:
                    raise AttributeError("INPUT_ERROR: Dirichlet bound condition with index "+str(idx)+" contain "+str(l1)+" value components and "+str(l2)+" derivative components!")
                else:
                    l = l1
            if l != systemsLen:
                raise AttributeError("INPUT_ERROR: Bound condition with index "+str(idx)+" contain "+str(l)+" value components instead "+str(systemsLen)+"!")
                            