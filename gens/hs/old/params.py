import sys

# python 2 or 3
if sys.version_info[0] > 2:

    from someFuncs import determineNameOfBoundary
    from someFuncs import getCellCountInClosedInterval
    from someFuncs import getRangesInClosedInterval

import logging

from copy import deepcopy as copy
from copy import copy as weak_copy

from string import Template

# for independet launching this module
#logging.basicConfig(level=logging.DEBUG)

# create logger that child of tester loger
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

        cellCountList = block.getCellCount(model.grid.gridStepX,
                                           model.grid.gridStepY,
                                           model.grid.gridStepZ)
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

        cellCountList = block.getCellCount(model.grid.gridStepX,
                                           model.grid.gridStepY,
                                           model.grid.gridStepZ)
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
            xstart, xend = model.grid.getXrange(block, initReg.xfrom, initReg.xto)
            ystart, yend = model.grid.getYrange(block, initReg.yfrom, initReg.yto)
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
                    ystart, yend = model.grid.getYrange(block, boundReg.yfrom, boundReg.yto)    
                    funcArr[ystart:yend, idxX] = initFuncNum                
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = model.grid.getYrange(block, boundReg.yfrom, boundReg.yto)           
                    funcArr[ystart:yend, idxX] = initFuncNum                    
                elif boundReg.side == 2:
                    idxY =  0
                    xstart, xend = model.grid.getXrange(block, boundReg.xfrom, boundReg.xto) 
                    funcArr[idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = model.getXrange(block, boundReg.xfrom, boundReg.xto)
                    funcArr[idxY, xstart:xend] = initFuncNum

        print("initFunc")
        print(funcArr)

        return(funcArr)

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
