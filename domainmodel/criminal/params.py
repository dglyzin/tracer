import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.criminal.abstractGenerator import BoundCondition, Connection
    from domainmodel.criminal.someFuncs import determineNameOfBoundary
    from domainmodel.criminal.someFuncs import getCellCountInClosedInterval
    from domainmodel.criminal.someFuncs import getRangesInClosedInterval

else:
    from abstractGenerator import BoundCondition, Connection
    from someFuncs import determineNameOfBoundary
    from someFuncs import getCellCountInClosedInterval
    from someFuncs import getRangesInClosedInterval

import logging

from copy import deepcopy as copy
from copy import copy as weak_copy

from string import Template

# for independet launching this module
#logging.basicConfig(level=logging.DEBUG)

# create logger that child of tests.tester loger
logger = logging.getLogger('tests.tester.criminal.tests_gen.params')

import numpy as np


class Dbg():
    def __init__(self, dbg, dbgInx):
        self.dbg = dbg
        self.dbgInx = dbgInx

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')


class Bound():
    def __init__(self):
        # self.tFuncName = tFuncName
        # self.tFuncNameDefault = tFuncNameDefault
        pass

    def gen_bound(self):
        pass
    
    def __repr__(self):
        if self.name == 'sides bound':
            s = "side %s | " % self.side
            s += "blockNumber %s | " % self.blockNumber
            s += "boundNumber %s | " % self.boundNumber
            s += "equationNumber %s |" % self.equationNumber
            s += "funcName %s | " % self.funcName
            s += "btype %s | " % self.btype
            s += "region %s" % self.region
        elif(self.name == 'vertex bound'):
            s = "sides %s | " % self.sides
            s += "blockNumber %s | " % self.blockNumber
            s += "boundNumber %s | " % self.boundNumber
            s += "equationNumber %s |" % self.equationNumber
            s += "funcName %s | " % self.funcName
            s += "btype %s " % self.btype
        return(s)


class Params():
    '''
    DESCRIPTION:
    If string for cpp out (from cppOutsForTerms.py)
    contain some params or
    If actions in Actions.py contain some params
    that params must be there initiated.
    Or they must be added in parser.__init__ method in
    according section.
    '''
    def __init__(self):

        # for debub
        self.debug = Dbg(True, 1)

        # for comment before each central function
        self.hatCf = dict()
        
        # for name of central functions
        self.namesCf = dict()

        # for compatibility reason
        # cannot work with terms like
        # sin(a*x+b)
        self.fromOld = False

    def postprocessing(self, out):
        def convert_delay(val, delays):
            '''
            DESCRIPTION:
            Find index of floating delay val.
            independently of order.
            Value is only important for order:
            For ex:
            [5.1, 1.5, 2.7]->
            [3, 1, 2]
            '''
            delays = copy(delays)
            delays.sort()

            # for debug
            # self.print_dbg("delay_list:", delays)

            return(delays.index(val)+1)

        # change all founded delay marker to
        # delay
        termData = self.dataTermVarsForDelay
        newTermData = {}
        
        for var in termData.keys():
            newTermData[var] = []
            for delay in termData[var]:
                # convert delays like:
                # 1.1 -> 1 (see convert_delay)
                delayConv = convert_delay(delay, termData[var])
                '''
                self.print_dbg("delays", termData[var])
                self.print_dbg("delay", delay)
                self.print_dbg("var", var)
                '''
                newTermData[var].append(delayConv)

                # if no delay then just return same result
                out = out.replace("arg_delay_"+var+'_'+str(delay),
                                  str(delayConv))
                # self.print_dbg("out", out)
        
        # simple format of delays (all vars in same list)
        self.delays = [delay for varDelays in newTermData.values()
                       for delay in varDelays]
        # remove dublicates from different vars (i.e. U,V)
        self.delays = list(set(self.delays))

        # thats prabobly beter:
        # self.delays = newTermData
        
        return(out)

    def fill_parameters(self, model):
        params = np.zeros((len(model.params)))
        for i, param in enumerate(model.params):
            params[i] = model.paramValues[0][param]

        params = params.astype('double')
        
        return(params)
        
    def fill_2d_func_idxs(self, model, functionMap):
        '''
        DESCRIPTION:
        functionMaps from set_params_for_dom_*
        '''

        block = model.blocks[0]

        cellCountList = block.getCellCount(model.gridStepX, model.gridStepY,
                                           model.gridStepZ)
        cellCount = cellCountList[0]*cellCountList[1]*cellCountList[2]

        zc, yc, xc = cellCountList[2], cellCountList[1], cellCountList[0]

        blockCompFuncArr = np.zeros(cellCount, dtype=np.int32)
        funcArr = blockCompFuncArr.reshape([yc, xc])

        print("Filling 2d main function array.")
        print("Function mapping for this block:")
        print(functionMap)
        xc = cellCountList[0]
        yc = cellCountList[1]
        print("size:")
        print("x")
        print(xc)
        print("y")
        print(yc)
        haloSize = model.getHaloSize()
        if haloSize > 1:
            raise AttributeError("Halosize>1 is not supported yet")

        # 1 fill center funcs
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["center"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        # side 0
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side0"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        # side 1
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side1"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        # side 2
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side2"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        # side 3
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side3"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        #2 fill edges
        # funcArr[0,0]       = functionMap["v02"]
        # funcArr[0,xc-1]    = functionMap["v12"]
        # funcArr[yc-1,0]    = functionMap["v03"]
        # funcArr[yc-1,xc-1] = functionMap["v13"]

        print("funcIdxs")
        print(funcArr)

        return(funcArr)

    def fill_2d_init_funcs(self, model):

        block = model.blocks[0]

        cellCountList = block.getCellCount(model.gridStepX, model.gridStepY,
                                           model.gridStepZ)
        cellCount = cellCountList[0]*cellCountList[1]*cellCountList[2]
        zc, yc, xc = cellCountList[2], cellCountList[1], cellCountList[0]

        blockInitFuncArr = np.zeros(cellCount, dtype=np.int32)

        funcArr = blockInitFuncArr.reshape([yc, xc])

        bdict = {"dirichlet": 0, "neumann": 1}

        print("Filling 2d initial function array.")
        xc = cellCountList[0]
        yc = cellCountList[1]

        # 1 fill default conditions
        funcArr[:] = block.defaultInitial

        # 2 fill user-defined conditions
        # 2.1 collect user-defines initial conditions that are used in this block
        usedIndices = 0
        usedInitNums = [block.defaultInitial]
        for initReg in block.initialRegions:
            if not (initReg.initialNumber in usedInitNums):
                usedInitNums.append(initReg.initialNumber)
        # 2.2 fill them    
        for initReg in block.initialRegions:
            initFuncNum = usedIndices + usedInitNums.index(initReg.initialNumber)
            xstart, xend = model.getXrange(block, initReg.xfrom, initReg.xto)
            ystart, yend = model.getYrange(block, initReg.yfrom, initReg.yto)            
            funcArr[ystart:yend, xstart:xend] = initFuncNum             

        print("Used init nums:")
        print(usedInitNums)

        # 3 overwrite with values that come from Dirichlet bounds
        # 3.1 collect dirichlet bound numbers that are used in this block
        usedIndices += len(usedInitNums)
        usedDirBoundNums = []
        for boundReg in block.boundRegions:
            if not (boundReg.boundNumber in usedDirBoundNums):
                if (model.bounds[boundReg.boundNumber].btype == bdict["dirichlet"]):
                    usedDirBoundNums.append(boundReg.boundNumber)

        usedDirBoundNums.sort()
        print("Used Dirichlet bound nums:")
        print(usedDirBoundNums)

        # 3.2 fill them
        for boundReg in block.boundRegions:
            if (model.bounds[boundReg.boundNumber].btype == bdict["dirichlet"]):
                initFuncNum = usedIndices + usedDirBoundNums.index(boundReg.boundNumber)
                if boundReg.side == 0:       
                    idxX = 0         
                    ystart, yend = model.getYrange(block, boundReg.yfrom, boundReg.yto)    
                    funcArr[ystart:yend, idxX] = initFuncNum                
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = model.getYrange(block, boundReg.yfrom, boundReg.yto)           
                    funcArr[ystart:yend, idxX] = initFuncNum                    
                elif boundReg.side == 2:
                    idxY =  0
                    xstart, xend = model.getXrange(block, boundReg.xfrom, boundReg.xto) 
                    funcArr[idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = model.getXrange(block, boundReg.xfrom, boundReg.xto)
                    funcArr[idxY, xstart:xend] = initFuncNum

        print("initFunc")
        print(funcArr)

        return(funcArr)

    def set_params_for_dom_centrals(self, model):
        '''
        DESCRIPTION:
        mapping equations to block parts.
        like
         center: [  [ 1, xfrom, xto, yfrom, yto],
        means equation[1] for part
         (xfrom, yfrom), (xto, yto)

        '''
        # check if functionMaps alredy exist:
        if 'functionMaps' not in self.__dict__:
            self.functionMaps = []
        
        dim = model.dimension

        def init_acc():
            '''
            Dont used here.
            '''
            if dim == 1:
                return(0)
            elif dim == 2:
                return([0, 0])

        def acc(eRegion, reservedSpace):
            '''
            DESCRIPTION:
            Accumulate equation regions area for checking
            either it enough or use default eqation.
            Dont used here
            '''
            if dim == 1:
                reservedSpace += eRegion.xto - eRegion.xfrom
            elif dim == 2:
                reservedSpace[0] += eRegion.xto - eRegion.xfrom
                reservedSpace[1] += eRegion.yto - eRegion.yfrom
            return(reservedSpace)

        def do_generate_default(reservedSpace, block):
            '''
            DESCRIPTION:
            Check use default or not.
            Dont used here.
            '''
            if dim == 1:
                return(block.sizeX > reservedSpace)
            elif dim == 2:
                return(block.sizeX > reservedSpace[0]
                       or
                       block.sizeY > reservedSpace[1])

        def get_ranges(eRegion):
            if dim == 1:
                ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto, model.gridStepX])
            elif dim == 2:
                ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto, model.gridStepX],
                                                   [eRegion.yfrom, eRegion.yto, model.gridStepY])
            return(ranges)

        for blockNumber, block in enumerate(model.blocks):

            blockFuncMap = {'center': []}
            for equation in self.equations:
                if equation.blockNumber == blockNumber:
                    eq_num = self.namesAndNumbers[equation.blockNumber].index(equation.funcName)
                    if equation.default:
                        blockFuncMap['center_default'] = eq_num
                    else:
                        ranges = get_ranges(equation.eRegion)
                        blockFuncMap['center'].append([eq_num]+ranges)
            '''
            # split equations at regions
            for eRegion in block.equationRegions:
                reservedSpace = acc(eRegion, reservedSpace)

                # for removing trivial cases
                cond = (eRegion.xfrom == eRegion.xto
                        and
                        (eRegion.xto == 0.0 or eRegion.xto == block.sizeX))

                
                if eRegion.equationNumber not in numsForSystems and not cond:
                    numsForSystems.append(eRegion.equationNumber)
                if not cond:
                    # see getRangesInClosedInterval description
                    ranges = get_ranges(eRegion)
                    # blockFuncMap['center'].append([eq_num] + ranges)
                    blockFuncMap['center'].append([numsForSystems.index(eRegion.equationNumber)] + ranges)
            
            # add default equation at remaining regions.
            if do_generate_default(reservedSpace, block):
                # add last as default
                blockFuncMap.update({'center_default': len(numsForSystems)})
                numsForSystems.append(block.defaultEquation)
            '''
            self.functionMaps.append(blockFuncMap)

    def set_params_for_dom_interconnects(self):
        '''
        DESCRIPTION:
        self.functionMaps must be exist.
        self.ics must be exist.
        self.funcNamesStack must be exist.
        self.namesAndNumbers must be exist.

        So use
         set_params_for_centrals      for self.funcNamesStack
         set_params_for_interconnects for self.funcNamesStack
                                       and self.ics
         set_params_for_bounds        for self.funcNamesStack
         set_params_for_dom_centrals  for self.functionMaps
         set_params_for_array         for namesAndNumbers
        first.
        '''
        # interconnect
        logger.debug("namesAndNumbers = %s" % (self.namesAndNumbers[0]))
        for ic in self.ics:
            sideName = "side"+str(ic.side)
            
            # count of interconnects for each block
            idx = self.namesAndNumbers[ic.blockNumber].index(ic.funcName)
            logger.debug("funcName=%s " % str(ic.funcName))
            logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))
            self.functionMaps[ic.blockNumber].update({sideName: idx})
  
    def set_params_for_dom_bounds(self, model):
        '''
        DESCRIPTION:
        self.functionMaps must be exist.
        self.bounds must be exist.
        self.funcNamesStack must be exist.
        self.namesAndNumbers must be exist.

        So use
         set_params_for_centrals      for self.funcNamesStack
         set_params_for_interconnects for self.funcNamesStack
         set_params_for_bounds        for self.funcNamesStack
                                      and self.bounds
         set_params_for_dom_centrals  for self.functionMaps
         set_params_for_array         for namesAndNumbers
        first.

        namesAndNumbers is copy of pBoundFuncs of
        getBlockBoundFuncArray function.
        It contain func names at according position
        and used for getting right number of equations in domain file.
        '''
        dim = model.dimension

        def get_idx(bound):
            '''
            DESCRIPTION:
            Get idx for bound.side. For both 1d and 2d.
            
            RETURN:
            for 1d 
            equation number
            for 2d
            [equation number, xfrom, xto, yfrom, yto]
            '''
            eq_num = self.namesAndNumbers[bound.blockNumber].index(bound.funcName)
            if dim == 1:
                idx = eq_num
            elif dim == 2:
                block = model.blocks[bound.blockNumber]
                if bound.side == 0:
                    xfrom = 0
                    xto = 0
                    yfrom = bound.region[0]
                    yto = bound.region[1]
                                        
                    intervalX = [xfrom, xto, model.gridStepX]
                    intervalY = [yfrom, yto, model.gridStepY]
                    ranges = getRangesInClosedInterval(intervalX, intervalY)

                    # because xfrom == xto == 0
                    # and Im(xfrom) == 0 and Im(xto) == 1
                    # make Im(xto) = 0 (==Im(xfrom))
                    # ranges[1] = ranges[0]

                elif(bound.side == 1):
                    xfrom = block.sizeX
                    xto = block.sizeX
                    yfrom = bound.region[0]
                    yto = bound.region[1]
                                        
                    intervalX = [xfrom, xto, model.gridStepX]
                    intervalY = [yfrom, yto, model.gridStepY]
                    ranges = getRangesInClosedInterval(intervalX, intervalY)

                    # because xfrom == xto == sizeX
                    # and Im(xfrom) == Im(sizeX) and Im(xto) == Im(sizeX)+1
                    # make Im(xfrom) = Im(sizeX)+1 (==Im(xto))
                    # ranges[0] = ranges[1]

                elif(bound.side == 2):
                    xfrom = bound.region[0]
                    xto = bound.region[1]
                    yfrom = 0
                    yto = 0
                    
                    intervalX = [xfrom, xto, model.gridStepX]
                    intervalY = [yfrom, yto, model.gridStepY]
                    ranges = getRangesInClosedInterval(intervalX, intervalY)

                    # because yfrom == yto == 0
                    # and Im(yfrom) == 0 and Im(yto) == 1
                    # make Im(yto) = 0 (==Im(yfrom))
                    # ranges[3] = ranges[2]

                elif(bound.side == 3):
                    xfrom = bound.region[0]
                    xto = bound.region[1]
                    yfrom = block.sizeY
                    yto = block.sizeY

                    intervalX = [xfrom, xto, model.gridStepX]
                    intervalY = [yfrom, yto, model.gridStepY]
                    ranges = getRangesInClosedInterval(intervalX, intervalY)

                    # because yfrom == yto == sizeY
                    # and Im(yfrom) == Im(sizeY) and Im(yto) == Im(sizeY)+1
                    # make Im(yfrom) = Im(sizeY)+1 (==Im(yto))
                    # ranges[2] = ranges[3]
                    
                idx = [eq_num] + ranges
            return(idx)

        # bounds vertex
        if dim == 2:
            for bound in self.bounds_vertex:
                # for compatibility with old version of saveDomain
                if bound.sides in [[2, 1], [3, 0]]:
                    vertexName = 'v%d%d' % (bound.sides[1], bound.sides[0])
                else:
                    vertexName = 'v%d%d' % (bound.sides[0], bound.sides[1])

                eq_num = self.namesAndNumbers[bound.blockNumber].index(bound.funcName)
                self.functionMaps[bound.blockNumber].update({vertexName: eq_num})

        # bounds sides
        for bound in self.bounds:
            sideName = "side"+str(bound.side)

            # for setDomain
            idx = get_idx(bound)
            logger.debug("funcName=%s " % str(bound.funcName))
            logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))

            old = self.functionMaps[bound.blockNumber]
            if sideName in old.keys():
                # if side exist
                self.functionMaps[bound.blockNumber][sideName].append(idx)
            else:
                # because in 2d side will be list
                if dim == 1:
                    self.functionMaps[bound.blockNumber].update({sideName: idx})
                elif dim == 2:
                    self.functionMaps[bound.blockNumber].update({sideName: [idx]})

    def set_params_for_array(self):
        '''
        DESCRIPTION:
        factorize funcNames into blockNumber's classes
        i.e. namesAndNumbers[blockNumber] = [names for blockNumber]

        self.funcNamesStack must exist.
        
        '''
        def get_number(funcName):
            '''
            DESCRIPTION:
            From funcName get blockNumber
            
            EXAMPLE:
            'Block0CentralFunction1' -> '0'
            '''
            # cut name Block from funcName
            tail = funcName[5:]
            blockNumber = []
            # find end of number
            for num in tail:
                if num in '0123456789':
                    blockNumber.append(num)
                else:
                    break
            return(blockNumber[0])

        # factorize funcNames into blockNumber's classes
        # i.e. namesAndNumbers[blockNumber] = [names for blockNumber]
        namesAndNumbers = {}
        for funcName in self.funcNamesStack:
            blockNumber = int(get_number(funcName))
            if blockNumber in namesAndNumbers.keys():
                namesAndNumbers[blockNumber].append(funcName)
            else:
                namesAndNumbers[blockNumber] = [funcName]

        self.namesAndNumbers = namesAndNumbers

    def set_params_for_definitions(self, model):
        '''
        DESCRIPTION:
        Fill params for definitions 1d template.
        '''

        # FOR addition parameters
        gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]

        # count of equation in each cell
        # (storage of each cell is count of equations in block)
        eqs = model.equations

        def get_cell_size(block):
            return(len(eqs[block.defaultEquation].system))

        def get_grid_offsets(block):
            try:
                # 3d
                return([block.offsetX, block.offsetY, block.offsetZ])
            except:
                try:
                    # 2d
                    return([block.offsetX, block.offsetY, 0])
                except:
                    # 1d
                    return([block.offsetX, 0, 0])

        def get_grid_sizes(block):
            try:
                # 3d
                return([block.sizeX, block.sizeY, block.sizeZ])
            except:
                try:
                    # 2d
                    return([block.sizeX, block.sizeY, 0])
                except:
                    # 1d
                    return([block.sizeX, 0, 0])
        # END FOR addition parameters

        # FOR ERRORS
        if len(gridStep) < 3:
            raise AttributeError("A list 'gridStep' should be consist of"
                                 + " values for ALL independent variables!"
                                 + " x, y, z")
        # END FOR ERRORS

        class Args():
            '''
            DESCRIPTION:
            Class for storage args data
            for code simplification reason.
            '''
            def __init__(self):
                pass

        defaultIndepVars = ['x', 'y', 'z']

        # FOR gridArgs
        gridArgs = []
        for i in range(len(gridStep)):
            gridArg = Args()
            gridArg.indepVar = defaultIndepVars[i]
            d = gridStep[i]
            gridArg.d = d
            gridArg.d2 = round(d * d, 5)
            gridArg.dm1 = round(1 / d)
            gridArg.dm2 = round(1 / (d * d))
            gridArgs.append(gridArg)
        # END FOR gridArgs

        # FOR define block (mainly with stride and counts)
        blocksArgs = []
        for blockNumber, block in enumerate(model.blocks):
           
            blockArgs = Args()
            blockArgs.blockNumber = blockNumber
            blockArgs.cellsize = get_cell_size(block)

            # for each var in vars grid step exist
            countOfVars = len(gridStep)

            # for counts
            counts = []
            for i in range(countOfVars):
                d = gridStep[i]
                sizeForIndepVar = get_grid_sizes(block)[i]
                countOfGridStepsInVar = getCellCountInClosedInterval(sizeForIndepVar, d)
                counts.append(countOfGridStepsInVar)

            # for strides
            strides = []
            for i in range(countOfVars):
                if i == 0:
                    stride = 1
                elif i == 1:
                    stride = counts[0]
                else:
                    # if i == 2
                    stride = counts[0] * counts[1]
                strides.append(stride)

            blockArgs.indepVars = defaultIndepVars
            blockArgs.counts = counts
            blockArgs.strides = strides
            blockArgs.offsets = get_grid_offsets(block)

            blocksArgs.append(blockArgs)
        # END FOR stride and counts

        self.gridArgs = gridArgs
        self.blocksArgs = blocksArgs
        self.paramsLen = len(model.params)
        self.timeStep = model.timeStep

    def set_params_for_centrals(self, model):
        '''
        DESCRIPTION:
        Fill params for centrals 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''
        dim = model.dimension

        def init_acc():
            if dim == 1:
                return(0)
            elif dim == 2:
                return([0, 0])

        def acc(eRegion, reservedSpace):
            '''
            DESCRIPTION:
            Accumulate equation regions area for checking
            either it enough or use default eqation.
            '''
            if dim == 1:
                reservedSpace += eRegion.xto - eRegion.xfrom
            elif dim == 2:
                reservedSpace[0] += eRegion.xto - eRegion.xfrom
                reservedSpace[1] += eRegion.yto - eRegion.yfrom
            return(reservedSpace)

        def do_generate_default(reservedSpace, block):
            '''
            DESCRIPTION:
            Check use default or not.
            '''
            if dim == 1:
                return(block.sizeX > reservedSpace)
            elif dim == 2:
                return(block.sizeX > reservedSpace[0]
                       or
                       block.sizeY > reservedSpace[1])

        tFuncName = Template('''Block${blockNumber}CentralFunction_Eqn${equationNumber}''')
        # FOR FILL params.equations
        equations = []

        for blockNumber, block in enumerate(model.blocks):
            reservedSpace = init_acc()

            # collect all equations for block
            # equationRegions should be sorted
            for eRegion in block.equationRegions:
                reservedSpace = acc(eRegion, reservedSpace)

                # for removing trivial cases
                cond = (eRegion.xfrom == eRegion.xto
                        and
                        (eRegion.xto == 0.0 or eRegion.xto == block.sizeX))

                # numsForSystems = [eq.number for eq in equations]
                # if eRegion.equationNumber not in numsForSystems and not cond:
                if not cond:
                    equation = copy(model.equations[eRegion.equationNumber])
                    equation.number = eRegion.equationNumber
                    equation.eRegion = eRegion
                    equation.dim = dim
                    equation.blockNumber = blockNumber
                    equation.funcName = tFuncName.substitute(blockNumber=blockNumber,
                                                             equationNumber=eRegion.equationNumber)
                    equation.default = False
                    logger.debug('blockNumber eqReg=%s' % str(blockNumber))

                    if equation.funcName not in [e.funcName for e in equations]:
                        equations.append(equation)

            # add default equation at remaining regions.
            if do_generate_default(reservedSpace, block):
                equation = copy(model.equations[block.defaultEquation])
                equation.number = block.defaultEquation
                equation.eRegion = None
                equation.dim = dim
                equation.blockNumber = blockNumber
                equation.funcName = tFuncName.substitute(blockNumber=blockNumber,
                                                         equationNumber=block.defaultEquation)
                equation.default = True
                logger.debug('blockNumber revSp=%s' % str(blockNumber))
                if equation.funcName not in [e.funcName for e in equations]:
                    equations.append(equation)

        self.equations = equations
        # END FOR FILL

        # FOR FuncArray
        funcNamesStack = [equation.funcName for equation in equations]

        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

        # FOR parsing
        for eq in equations:
            eq.values = eq.system

    def set_params_for_interconnects(self, model):
        '''
        DESCRIPTION:
        Fill params for interconnects 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''
        # FOR FILL params.ics
        ics = []

        def choice_equation_num(test, block):
            '''
            DESCRIPTION:
            Choice equation number from equationRegions
            if any satisfy the test, else choice default.
            '''
            for eRegion in block.equationRegions:
                if test(eRegion):
                    equationNum = eRegion.equationNumber
                    break
            else:
                equationNum = block.defaultEquation
            return(equationNum)

        for blockNumber, block in enumerate(model.blocks):
            for iconn in model.interconnects:
                # for closed block
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

                    # find equation
                    # for first block (one side of closed block)
                    side_test = lambda eRegion: coord1(eRegion) == Range1
                    equationNum1 = choice_equation_num(side_test, block)

                    # find equation
                    # for second block (other side of closed block)
                    side_test = lambda eRegion: coord2(eRegion) == Range2
                    equationNum2 = choice_equation_num(side_test, block)

                    equation1 = model.equations[equationNum1]
                    equation2 = model.equations[equationNum2]

                    funcName1 = ("Block" + str(blockNumber) + "Interconnect__Side"
                                 + str(iconn.block1Side) + "_Eqn" + str(equationNum1))
                    funcName2 = ("Block" + str(blockNumber) + "Interconnect__Side"
                                 + str(iconn.block2Side) + "_Eqn" + str(equationNum2))

                    ic1 = Connection(0, '0', iconn.block2Side, [],
                                     equationNum2, equation2, funcName2)
                    ic1.boundName = determineNameOfBoundary(iconn.block2Side)
                    ic1.blockNumber = blockNumber

                    ic2 = Connection(1, '0', iconn.block1Side, [],
                                     equationNum1, equation1, funcName1)
                    ic2.boundName = determineNameOfBoundary(iconn.block1Side)
                    ic2.blockNumber = blockNumber

                    ics.append(ic1)
                    ics.append(ic2)
                    continue

                # for differ blocks
                elif blockNumber in [iconn.block1, iconn.block2]:
                    if iconn.block1 == blockNumber and iconn.block2 != blockNumber:
                        # case differ 1
                        side = iconn.block1Side
                    elif iconn.block2 == blockNumber and iconn.block1 != blockNumber:
                        # case differ 2
                        side = iconn.block2Side
                    # len(ics for block) 
                    firstIndex = len(ics)
                    Range = (side == 1) * block.sizeX
                    coord = lambda region: (side == 0) * region.xfrom + (side == 1) * region.xto

                    # find equation for block
                    side_test = lambda eRegion: coord(eRegion) == Range
                    equationNum = choice_equation_num(side_test, block)

                    equation = model.equations[equationNum]

                    funcName = ("Block" + str(blockNumber) + "Interconnect__Side"
                                + str(side) + "_Eqn" + str(equationNum))
                    ic = Connection(firstIndex, '0', side, [],
                                    equationNum, equation, funcName)
                    ic.boundName = determineNameOfBoundary(side)
                    ic.blockNumber = blockNumber
                    
                    # each block can connect to many other block
                    # let other block discribe interconnect in
                    # that case
                    icsOld = [icl.funcName for icl in ics]
                    #logger.debug("icsOld = %s" % str(icsOld))
                    if ic.funcName not in icsOld:
                        ics.append(ic)
                else:
                    continue

        self.ics = ics
        # END FOR FILL

        # FOR FuncArray
        funcNamesStack = [ic.funcName for ic in ics]

        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

    def set_params_for_bounds_2d(self, model):
        '''
        DESCRIPTION:
        Fill params for bound 2d template.
        '''

        # FOR FILL params.bounds
        self.bounds = []

        # FOR helpful functions:
        def test_region_exist(eRegion, side):
            '''
            DESCRIPTION:
            Test if equation region exist for this side.
            '''
            if side == 0:
                # test for [0, y]
                return(eRegion.xfrom == 0.0)
            elif(side == 3):
                # test for [x, y_max]
                return(eRegion.yto == block.sizeY)
            elif(side == 1):
                # test for [x_max, y]
                return(eRegion.xto == block.sizeX)
            elif(side == 2):
                # test for [x, 0]
                return(eRegion.yfrom == 0.0)

        # templates for funcName
        tFuncName = Template('''Block${blockNumber}${btype}${side}_${boundNumber}__Eqn${equationNumber}''')
        tFuncNameDefault = Template('''Block${blockNumber}DefaultNeumann__Bound${side}__Eqn${equationNumber}''')
        tFuncNameVertex = Template('''Block${blockNumber}Default_Vertex${side_0}_${side_1}__Eqn${equationNumber}''')
        
        def transform_side(side, block):
            '''
            DESCRIPTION:
            Return
            [interval | for each equationRegion from eRegionsForSide
                           if equationRegion intersects with bRegion [1]
                              where interval.name will be equal equationRegion.equationNumber
                                    (or dem for default)]
 
            [1]  (see Interval class for more about interval's intersection)
            
            den             - default equation number

            INPUT:
            eRegionsForSide - equationRegions for side
            bRegion         - boundRegions
            '''
            self.debug.print_dbg("FROM transform_side")

            den = block.defaultEquation
            if side in [0, 1]:
                # case for [0, y] or [x_max, y]

                _from = lambda region: region.yfrom
                _to = lambda region: region.yto
                block_size = block.sizeY

            elif(side in [3, 2]):
                # case for [x, y_max] or [x, 0]

                _from = lambda region: region.xfrom
                _to = lambda region: region.xto
                block_size = block.sizeX

            # find equation regions for side
            eRegionsForSide = [eRegion for eRegion in block.equationRegions
                               if test_region_exist(eRegion, side)]

            self.debug.print_dbg("eRegionsForSide")
            self.debug.print_dbg(eRegionsForSide)

            # find bound region for side
            bRegionsForSide = [bRegion for bRegion in block.boundRegions
                               if bRegion.side == side]

            self.debug.print_dbg("bRegionsForSide")
            self.debug.print_dbg(bRegionsForSide)

            sInterval = Interval([0.0, block_size], name={'b': None, 'e': den})

            bIntervals = [Interval([_from(bRegion), _to(bRegion)],
                                   name={'b': bRegion.boundNumber})
                          for bRegion in bRegionsForSide]
            
            bIntervals = sInterval.split_all(bIntervals, [])

            self.debug.print_dbg("bIntervals")
            self.debug.print_dbg(bIntervals)
            
            '''
            for bInterval in bIntervals:
                print_dbg(bInterval.name)
            '''
            eIntervals = [Interval([_from(eRegion), _to(eRegion)],
                                   name={'e': eRegion.equationNumber})
                          for eRegion in eRegionsForSide]

            self.debug.print_dbg("eIntervals")
            self.debug.print_dbg(eIntervals)
            
            oIntervals = []
            for bInterval in bIntervals:
                oIntervals.extend(bInterval.split_all(copy(eIntervals), []))
            
            self.debug.print_dbg("for side", side)
            self.debug.print_dbg("oIntervals")
            self.debug.print_dbg(oIntervals)
            
            new_side = {'side': side,
                        'blockNumber': block.blockNumber,
                        'side_data': oIntervals}
            return(new_side)
  
        def transform_vertex(vertex, sides, block):
            blockNumber = block.blockNumber
            side_left = [side for side in sides
                         if (side['side'] == vertex[0])
                         and (side['blockNumber'] == blockNumber)][0]
            side_right = [side for side in sides
                          if (side['side'] == vertex[1])
                          and (side['blockNumber'] == blockNumber)][0]

            # choice first or last region of side
            # according vertex position in block
            if vertex == [0, 2]:
                # vertex in [0, 0]
                vertex_data = [side_left['side_data'][0].name,
                               side_right['side_data'][0].name]
            if vertex == [2, 1]:
                # vertex in [x_max, 0]
                vertex_data = [side_left['side_data'][-1].name,
                               side_right['side_data'][0].name]
            if vertex == [1, 3]:
                # vertex in [x_max, y_max]
                vertex_data = [side_left['side_data'][-1].name,
                               side_right['side_data'][-1].name]
            if vertex == [3, 0]:
                # vertex in [0, y_max]
                vertex_data = [side_left['side_data'][0].name,
                               side_right['side_data'][-1].name]

            new_vertex = {'sides': vertex,
                          'blockNumber': block.blockNumber,
                          'vertex_data': vertex_data,
                          'side_left': side_left,
                          'side_right': side_right}
            return(new_vertex)

        def get_btype_name(boundNumber):
            '''
            DESCRIPTION:
            Get string name of bound type for funcName.
            '''
            btype = model.bounds[boundNumber].btype
            if btype == 1:
                return("Neumann__Bound")
            elif(btype == 0):
                return("Dirichlet__Bound")

        def make_bounds(side):
            '''
            DESCRIPTION:
            Create funcName, outputValues and equation (for parser)
            boundName for comment.
            side is out of transform_side
            side =
            {'side': side,
             'blockNumber': block.blockNumber,
             'side_data': oIntervals}
               where oIntervals =
                     {Interval([x, y], name={'b': bval, 'e', eval})}
            '''
            bounds = []
            for region in side['side_data']:

                bound = Bound()
                bound.name = 'sides bound'
                bound.side = side['side']
                bound.blockNumber = side['blockNumber']
                bound.boundNumber = region.name['b']
                bound.equationNumber = region.name['e']
                bound.region = region

                if bound.boundNumber is not None:
                    make_bounds_for_region(bound)
                else:
                    make_bounds_for_default(bound)
                bounds.append(bound)
            return(bounds)

        def make_bounds_for_region(bound):
            '''
            DESCRIPTION:
            Make
            bound.funcName,
            bound.values,
            bound.equation (for parser)
            bound.boundName for comment.

            Bound must contain:
            blockNumber,
            side,
            boundNumber,
            equationNumber.
            '''
            bNumber = bound.boundNumber

            # FOR make funcName from template
            funcName = tFuncName.substitute(blockNumber=bound.blockNumber,
                                            btype=get_btype_name(bNumber),
                                            side=bound.side,
                                            boundNumber=bNumber,
                                            equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            # FOR equation

            equation = model.equations[bound.equationNumber]
            bound.equation = equation
            # END FOR

            # FOR make outputValues

            btype = model.bounds[bNumber].btype
            bound.btype = btype
            
            if btype == 0:
                # for Dirichlet bound
                outputValues = list(model.bounds[bNumber].derivative)
            else:
                # for Neumann bound
                outputValues = list(model.bounds[bNumber].values)

                # special for Neumann bound
                if bound.side == 0 or bound.side == 2:
                    for idx, value in enumerate(outputValues):
                        outputValues.pop(idx)
                        outputValues.insert(idx, '-(' + value + ')')

            bound.values = outputValues
            # END FOR

            # for comment
            bound.boundName = determineNameOfBoundary(bound.side)

            return(bound)

        def make_bounds_for_default(bound):
            '''
            DESCRIPTION:
            Make
            bound.funcName,
            bound.values,
            bound.equation (for parser)
            bound.boundName for comment.

            Bound must contain:
            blockNumber,
            side,
            boundNumber,
            equationNumber.
            '''
            
            # FOR make funcName for defaults
            funcName = tFuncNameDefault.substitute(blockNumber=bound.blockNumber,
                                                   side=bound.side,
                                                   equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            bound.btype = 0

            # for equation
            bound.equation = model.equations[bound.equationNumber]
            
            # for values
            # bound.values = len(bound.equation.system) * ['0.0']
            block = model.blocks[bound.blockNumber]
            try:
                bound.values = list(model.bounds[block.defaultBound].values)
            except:
                raise BaseException(".json file has no DefaultBound key")
            # for comment
            bound.boundName = determineNameOfBoundary(bound.side)
            
            return(bound)

        def make_vertex(vertex, bounds):
            '''
            DESCRIPTION:
            Create funcName, outputValues and equation (for parser)
            boundName for comment.
            vertex is out of transform_vertex
            vertex =
            {'sides': [2, 1],
             'blockNumber': block.blockNumber,
             'vertex_data': vertex_data,
             'side_left': side_left,
             'side_right': side_right}
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

            '''

            # FOR find bound side for vertex left side (always)
            # i.e. for [2, 1] use bound side 2 data

            if vertex['sides'] == [0, 2]:
                # vertex in [0, 0]
                # first region of side 0
                region = vertex['side_left']['side_data'][0]
            if vertex['sides'] == [2, 1]:
                # vertex in [x_max, 0]
                # last region of side 2
                region = vertex['side_left']['side_data'][-1]
            if vertex['sides'] == [1, 3]:
                # vertex in [x_max, y_max]
                # last region of side 1
                region = vertex['side_left']['side_data'][-1]

            if vertex['sides'] == [3, 0]:
                # vertex in [0, y_max]
                # first region of side 3
                region = vertex['side_left']['side_data'][0]

            bound_side = [bound for bound in bounds
                          if bound.side == vertex['sides'][0]
                          and bound.blockNumber == vertex['blockNumber']
                          and bound.region == region][0]
            # END FOR

            bound = Bound()
            bound.name = 'vertex bound'
            bound.sides = vertex['sides']
            bound.blockNumber = vertex['blockNumber']

            # data of left side (with index 0)
            bound.boundNumber = vertex['vertex_data'][0]['b']
            bound.equationNumber = vertex['vertex_data'][0]['e']

            bound.bound_side = bound_side

            # FOR make funcName for defaults
            funcName = tFuncNameVertex.substitute(blockNumber=bound.blockNumber,
                                                  side_0=bound.sides[0],
                                                  side_1=bound.sides[1],
                                                  equationNumber=bound.equationNumber)
            bound.funcName = funcName
            # END FOR

            # FOR PARSER
            bound.btype = bound_side.btype
            bound.equation = bound_side.equation
            bound.values = bound_side.values
            # END FOR
            
            return(bound)

        def check_interconnect_exist(self, side, blockNumber):
            '''
            DESCRIPTION:
            Check if interconnect for this side exist in ics.
            
            '''
            
            if 'ics' in self.__dict__.keys():
                icSides = [ic.side for ic in self.ics
                           if ic.blockNumber == blockNumber]
                if side in icSides:
                    # if exist then no boundary needed
                    #logger.debug('icSides = %s' % str(icSides))
                    #logger.debug('blockNumber = %s' % str(blockNumber))
                    #logger.debug('side = %s' % str(side))
                    return(True)
                else:
                    return(False)

        # END FOR

        # main code:
        # make long necessary obvious thing:
        for blockNumber, block in enumerate(model.blocks):
            block.blockNumber = blockNumber

        # transform sides to regions like list
        new_sides = [transform_side(side, block)
                     for block in model.blocks
                     for side in [2, 3, 0, 1]]
        
        #             if not check_interconnect_exist(self, side,
        #                                             block.blockNumber)]
        '''
        for blockNumber, block in enumerate(model.blocks):

            sides = [2, 3, 0, 1]

            for side in sides:

                # check if interconnect for this side exist
                if check_interconnect_exist(self, side,  blockNumber):
                    # if exist then no boundary needed
                    continue

                # FOR region bounds
                
                new_side = transform_side(side, block)
                new_sides.append(new_side)
        '''

        self.new_sides = new_sides
        
        # make bounds for side
        self.bounds.extend([bound for side in new_sides
                            for bound in make_bounds(side)
                            if bound not in self.bounds])
        
        # transform vertex:
        new_vertexs = [transform_vertex(vertex, new_sides, block)
                       for block in model.blocks
                       for vertex in [[0, 2], [2, 1], [1, 3], [3, 0]]]
        '''
        # main code:
        for blockNumber, block in enumerate(model.blocks):

            vertexs = [[0, 2], [2, 1], [1, 3], [3, 0]]

            for vertex in vertexs:

                # FOR region bounds
                
                new_vertex = transform_vertex(vertex, new_sides, block)
                self.new_vertexs.append(new_vertex)
        '''
        self.new_vertexs = new_vertexs

        # make bounds for vertex
        self.bounds_vertex = [make_vertex(vertex, self.bounds)
                              for vertex in self.new_vertexs]
        # END FOR FILL
        
        # FOR FuncArray
        funcNamesStack = [bound.funcName for bound in self.bounds]
        funcNamesStack.extend([bound.funcName for bound in self.bounds_vertex])

        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            '''
            for funcName in funcNamesStack:
                if funcName not in self.funcNamesStack:
                    self.funcNamesStack.append(funcName)
            '''
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

    def set_params_for_bounds(self, model):
        '''
        DESCRIPTION:
        Fill params for bound 1d template.
        
        TODO:
        Fill parsedValues from parser.
        '''

        # FOR FILL params.bounds
        self.bounds = []

        def test(region):
            '''
            DESCRIPTION:
            Test if region exist for this side.
            '''
            if side == 0:
                # test for left side
                return(region.xfrom == 0.0)
            else:
                # test for right side
                return(region.xto == block.sizeX)

        for blockNumber, block in enumerate(model.blocks):

            sides = [0, 1]
            for side in sides:
                # check if interconnect for this side exist
                if 'ics' in self.__dict__.keys():
                    icSides = [ic.side for ic in self.ics
                               if ic.blockNumber == blockNumber]
                    if side in icSides:
                        # if exist then no boundary needed
                        #logger.debug('icSides = %s' % str(icSides))
                        #logger.debug('blockNumber = %s' % str(blockNumber))
                        #logger.debug('side = %s' % str(side))
                        continue

                # find equation number for side or use default
                regsEqNums = [eqReg.equationNumber for eqReg in block.equationRegions
                              if test(eqReg)]
                equationNum = regsEqNums[0] if len(regsEqNums) > 0 else block.defaultEquation
                equation = model.equations[equationNum]

                # find bound region for side or use default
                regionsForSide = [bRegion for bRegion in block.boundRegions
                                  if bRegion.side == side]
                if len(regionsForSide) > 0:
                    # if exist special region for that side
                    region = regionsForSide[0]
                    boundNumber = region.boundNumber
                    btype = model.bounds[boundNumber].btype
                    if btype == 0:
                        # for Dirichlet bound
                        funcName = ("Block" + str(blockNumber) + "Dirichlet__Bound"
                                    + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum))
                        outputValues = list(model.bounds[boundNumber].derivative)
                    elif btype == 1:
                        # for Neumann bound
                        funcName = ("Block" + str(blockNumber) + "Neumann__Bound"
                                    + str(side) + "_" + str(boundNumber) + "__Eqn" + str(equationNum))
                        outputValues = list(model.bounds[boundNumber].values)
                        
                        # special for Neumann bound
                        if side == 0 or side == 2:
                            for idx, value in enumerate(outputValues):
                                outputValues.pop(idx)
                                outputValues.insert(idx, '-(' + value + ')')
                    values = list(outputValues)
                else:
                    # if not, use default
                    funcName = ("Block" + str(blockNumber) + "DefaultNeumann__Bound"
                                + str(side) + "__Eqn" + str(equationNum))
                    values = len(equation.system) * ['0.0']
                    btype = 1
                    boundNumber = -1
                bound = BoundCondition(values, btype, side, [], boundNumber,
                                       equationNum, equation, funcName,
                                       block, blockNumber = blockNumber)
                bound.boundName = determineNameOfBoundary(side)
                self.bounds.append(bound)
        # END FOR FILL
        
        # FOR FuncArray
        funcNamesStack = [bound.funcName for bound in self.bounds]
        
        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            '''
            for funcName in funcNamesStack:
                if funcName not in self.funcNamesStack:
                    self.funcNamesStack.append(funcName)
            '''
            self.funcNamesStack.extend(funcNamesStack)
        else:
            self.funcNamesStack = funcNamesStack
        # END FOR

    def set_params_for_parameters(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp.
        for cppOutsForGenerators.get_out_for_parameters

        USED PARAMETERS:
        model.params
        model.paramValues
        '''
        self.parameters = model.params
        self.parametersVal = model.paramValues[model.defaultParamsIndex]

    def set_params_for_initials(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp initial and Dirichlet functions.
        for cppOutsForGenerators.get_out_for_initials

        USED PARAMETERS:
        model.blocks
        model.initials
        model.bounds
        '''
        # FOR FILL model.blocks
        for block in model.blocks:

            # for Dirichlet
            # set() used for removing duplicates
            fDirichletIndexes = list(
                set(
                    [bR.boundNumber for bR in block.boundRegions
                     if (model.bounds[bR.boundNumber] == 0)]))
            block.fDirichletIndexes = fDirichletIndexes

            # for initials
            block.initialIndexes = [iR.initialNumber for iR in block.initialRegions
                                    if iR.initialNumber != block.defaultInitial]
            block.initials = [model.initials[idx] for idx in block.initialIndexes]
            block.bounds = [model.bounds[idx] for idx in block.fDirichletIndexes]
        self.blocks = model.blocks
        # END FOR FILL

    def init_params_general(self, blockNumber, dim):
        # parameters fill
        self.dim = dim
        if blockNumber is not None:
            self.blockNumber = blockNumber
        else:
            self.blockNumber = 0
        self.dim = dim
            
    def set_hat_for_all_cf(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        '''
        self.cf_hat_common = ('\n//========================='
                              + 'CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER '
                              + str(blockNumber)
                              + '========================//\n\n')
    
    def set_stride_map(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        self.dim
        '''
        self.strideMap = dict()
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            self.strideMap[var] = ('Block' + str(blockNumber)
                                   + 'Stride' + var.upper())
        
    def get_hat_for_cf(self, blockNumber, eqNumber):
        '''
        USED FUNCTIONS
        blockNumber
        equationNumber
        self.dim
        '''
        text = ('//'+str(eqNumber)
                + ' central function for '
                + str(self.dim)
                + 'd model for block with number '
                + str(blockNumber)
                + '\n')

        self.hatCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_name(self, blockNumber, eqNumber):
        text = ('Block' + str(blockNumber)
                + 'CentralFunction'
                + str(eqNumber))  # numsForEquats[num]
        self.namesCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_signature(self, blockNumber, name):
        '''
        USED FUNCTIONS:
        self.dim
        blockNumber
        name - function name
        '''
        signatureStart = 'void ' + name + '(double* result, double** source, double t,'
        signatureMiddle = ''
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            signatureMiddle = signatureMiddle + ' int idx' + var.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'

        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ('
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            idx = idx + ' + idx' + var.upper() + ' * ' + self.strideMap[var]
        idx = idx + ') * Block' + str(blockNumber) + 'CELLSIZE;\n'
        
        return list([signature, idx])
    
    def rest(self):
        delays = []
                
        equationRightHandSide = parser.parseMathExpression(equationString, variables,
                                                           self.params, self.userIndepVars,
                                                           delays)
        function.extend([
            b.generateRightHandSideCodeDelay(blockNumber, variables[i],
                                             equationRightHandSide,
                                             self.userIndepVars, variables,
                                             self.params, list(),
                                             delays)])
        # for setDomain
        if len(delays) > 0:
            self.delays.extend(delays)
            
        function.extend(['}\n\n'])
        
        return ''.join(function), arrWithFuncName


class Property(object):
    '''
    DESCRIPTION:
    Descriptor for Interval.
    '''
    def __init__(self, attrName):
        self.attrName = attrName
    
    def __get__(self, instance, owner=None):
        '''
        DESCRIPTION:
        Instance is instance of UseProperty class.
        getattr get atrName of instance UseProperty class.
        '''
        # print("get")
        # print(instance)
        return(getattr(instance, self.attrName))
    
    def __set__(self, instance, value):
        '''
        DESCRIPTION:
        If value is dict it update instance.attrName dict
           if self.attrName is not dict, it replace it
              by dict value
        else
           it just set instance.attrName by value. 
        '''
        # print("set")
        if type(value) is not dict:
            return(setattr(instance, self.attrName, value))

        old_data = getattr(instance, self.attrName)
        
        # print("old_data")
        # print(old_data)
        
        if type(old_data) == dict:
            new_data = copy(old_data)
            new_data.update(value)
        else:
            new_data = value

        # print("new_data")
        # print(new_data)
        
        return(setattr(instance, self.attrName, new_data))


class Interval(list):

    # descriptor at self._name
    name = Property("_name")

    def __init__(self, _list, name=0):
        # for debug
        self.debug = Dbg(False, 3)

        list.__init__(self, _list)
                
        self._name = name
        
    def __contains__(self, x):
        if self[0] < x < self[1]:
            return(True)
        else:
            return(False)

    def split_all(self, intervals_list, result=[]):
        '''
        DESCRIPTION:
        Split self at regions with names interval.name
        where interval in intervals_list.

        Example:
        >>> i, j, k = pms.Interval([1, 2], name='i'),\
        pms.Interval([2, 3], name='j'),\
        pms.Interval([1.5, 2.5],name='k')
        
        >>> t = k.split_all([i, j])

        >>> t[0], t[0].name
        ([1.5, 2], 'i')

        >>> t[1], t[1].name
        ([2, 2.5], 'j')

        '''
        self.debug.print_dbg("FROM Interval.split_all")

        if len(result) == 0:
            result.append(self)

        if len(intervals_list) == 0:
            self.debug.print_dbg("result")
            self.debug.print_dbg(result)
            return(result)
        
        first, rest = intervals_list[0], intervals_list[1:]

        new_res = []
        for res in result:
            new_res.extend(res.split(first))
                
        return(self.split_all(rest, new_res))

    def split(self, interval):
        '''
        DESCRIPTION:
        Split self at regions with names from
        original and interval.name.
        
        RETURN:
        Never empty.

        Example:
        >>> a = Interval([1, 3], name='a')
        >>> b = Interval([1, 2], name='b')
        
        >>> cs = a.split(b)
        >>> cs[0], cs[0].name
        ([1, 2], 'a')

        >>> cs[1], cs[1].name
        ([2, 3], 'b')
        '''
        interval_from = self

        if (interval[0] not in interval_from and
            interval[1] not in interval_from):
            # if interval not in interval_from

            # if interval_from not in interval
            if (interval[1] <= interval_from[0] or
                interval[0] >= interval_from[1]):
                # do nothing
                return([interval_from])            
            else:
                # if interval_from in interval
                
                # rename interval_from
                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                interval_from.name = interval_from.name
                interval_from.name = interval.name
                return([interval_from])

        elif(interval[0] in interval_from):
            # if interval intersects interval_from by left side

            result = []
            iLeft = Interval([interval_from[0], interval[0]])
            iLeft.name = interval_from.name
            result.append(iLeft)

            if(interval[1] in interval_from):
                # if interval in interval_from

                iRight = Interval([interval[1], interval_from[1]])
                iRight.name = interval_from.name

                iMidle = Interval([interval[0], interval[1]])

                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                iMidle.name = interval_from.name
                iMidle.name = interval.name

                result.append(iMidle)
                result.append(iRight)
            else:
                # if right side of interval not in interval_from
                iRight = Interval([interval[0], interval_from[1]])

                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                iRight.name = interval_from.name
                iRight.name = interval.name

                result.append(iRight)
            return(result)

        elif(interval[1] in interval_from):
            # if interval intersects interval_from by right side

            iLeft = Interval([interval_from[0], interval[1]])

            # if name is dict update it twice
            # else just set interval.name
            # (see Property.__set__)
            iLeft.name = interval_from.name
            iLeft.name = interval.name

            iRight = Interval([interval[1], interval_from[1]])
            iRight.name = interval_from.name
            return([iLeft, iRight])


class TestCase():

    def __init__(self):
        # for debug
        self.debug = Dbg(True, 1)

        self.tests_cases_for_interval = [
            "[0, 10];[0, 3];[5, 7]",  # common
            "[0, 10];[0, 3];[5, 13]",  # right too far
            "[2.5, 10];[0, 3];[5, 7]",  # left too far
            "[0, 10];[0, 3];[3, 7]",  # common point
            "[1, 10];[0, 1];[5, 7]"  # left intersects in point
        ]
        
        self.tests_results_for_interval = [
            # case 0: "[0, 10];[0, 3];[5, 7]"
            [Interval([0, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)],

            # case 1: "[0, 10];[0, 3];[5, 13]"
            [Interval([0, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 10], name=2)],

            # case 2: "[2.5, 10];[0, 3];[5, 7]"
            [Interval([2.5, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)],

            # case 3: "[0, 10];[0, 3];[3, 7]"
            [Interval([0, 3], name=1),
             Interval([3, 7], name=2),
             Interval([7, 10], name=0)],
            
            # case 4: "[1, 10];[0, 1];[5, 7]"
            [Interval([1, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)]
        ]

        self.tests_results_for_interval_dict = [
            # case 0: "[0, 10];[0, 3];[5, 7]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],

            # case 1: "[0, 10];[0, 3];[5, 13]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 10], name={'num': 2})],

            # case 2: "[2.5, 10];[0, 3];[5, 7]"
            [Interval([2.5, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],

            # case 3: "[0, 10];[0, 3];[3, 7]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],
            
            # case 4: "[1, 10];[0, 1];[5, 7]"
            [Interval([1, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})]
        ]

    def tests_intervals_dict(self):

        tests_cases = self.tests_cases_for_interval
        tests_results = self.tests_results_for_interval_dict

        for input_string in tests_cases:
            res = self.interval_interface_dict(input_string)

            # check test
            assert(res == tests_results[tests_cases.index(input_string)])

            # print result
            self.debug.print_dbg("for ", input_string)
            self.debug.print_dbg('res = ')
            for r in res:
                self.debug.print_dbg("name %s val %s " % (str(r.name), str(r)))
        return(True)

    def interval_interface_dict(self, input_string="[0, 10];[0, 3];[5, 7]"):
        ivs = [Interval(eval(sInterval), name={'num': num})
               for num, sInterval in enumerate(input_string.split(';'))]
        return(ivs[0].split_all(ivs[1:], []))

    def tests_intervals(self):

        tests_cases = self.tests_cases_for_interval
        tests_results = self.tests_results_for_interval

        for input_string in tests_cases:
            res = self.interval_interface(input_string)

            # check test
            assert(res == tests_results[tests_cases.index(input_string)])

            # print result
            self.debug.print_dbg("for ", input_string)
            self.debug.print_dbg('res = ')
            for r in res:
                self.debug.print_dbg("name %s val %s " % (str(r.name), str(r)))
            return(True)

    def interval_interface(self, input_string="[0, 10];[0, 3];[5, 7]"):
        ivs = [Interval(eval(sInterval), name=num)
               for num, sInterval in enumerate(input_string.split(';'))]
        return(ivs[0].split_all(ivs[1:], []))
        
