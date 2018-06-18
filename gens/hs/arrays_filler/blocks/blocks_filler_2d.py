import numpy as np

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.blocks_filler_2d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('blocks_filler_2d')
logger.setLevel(level=log_level)
'''

bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def fill2dInitFuncs(self, funcArr, block, blockSize):
        logger.info("Filling 2d initial function array.")

        model = self.net.model
        getXrange = model.grid.base.getXrange
        getYrange = model.grid.base.getYrange

        xc = blockSize[0]
        yc = blockSize[1]

        logger.info("1 fill default conditions")
        funcArr[:] = 0  # block.defaultInitial
        usedIndices = 0

        logger.info("2 fill user-defined conditions")
        logger.info("2.1 collect user-defines initial conditions")
        # that are used in this block
        usedInitNums = [block.defaultInitial]
        for initReg in block.initialRegions:
            if not (initReg.initialNumber in usedInitNums):
                usedInitNums.append(initReg.initialNumber)

        logger.info("2.2 fill them")
        for initReg in block.initialRegions:
            initFuncNum = (usedIndices
                           + usedInitNums.index(initReg.initialNumber))
            xstart, xend = getXrange(block, initReg.xfrom, initReg.xto)
            ystart, yend = getYrange(block, initReg.yfrom, initReg.yto)
            funcArr[ystart:yend, xstart:xend] = initFuncNum
                
        logger.debug("Used init nums:")
        logger.debug(usedInitNums)
        
        logger.info("3 overwrite with values that come from Dirichlet bounds")
        logger.info("3.1 collect dirichlet bound numbers")
        #  that are used in this block
        usedIndices += len(usedInitNums)
        usedDirBoundNums = []
        for boundReg in block.boundRegions:
            if not (boundReg.boundNumber in usedDirBoundNums):
                bound_btype = model.bounds[boundReg.boundNumber].btype
                if (bound_btype == bdict["dirichlet"]):
                    usedDirBoundNums.append(boundReg.boundNumber)
        usedDirBoundNums.sort()
        logger.debug("Used Dirichlet bound nums:")
        logger.debug(usedDirBoundNums)
        
        logger.info("3.2 fill them")
        for boundReg in block.boundRegions:
            bound_btype = self.dmodel.bounds[boundReg.boundNumber].btype
            if (bound_btype == bdict["dirichlet"]):
                initFuncNum = (usedIndices
                               + usedDirBoundNums.index(boundReg.boundNumber))
                if boundReg.side == 0:
                    idxX = 0
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    funcArr[ystart:yend, idxX] = initFuncNum
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    funcArr[ystart:yend, idxX] = initFuncNum
                elif boundReg.side == 2:
                    idxY = 0
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    funcArr[idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    funcArr[idxY, xstart:xend] = initFuncNum

    def fill2dCompFuncs(self, funcArr, block, functionMap, blockSize):
        logger.info("Filling 2d main function array.")
        
        logger.debug("Function mapping for this block:")
        logger.debug(functionMap)

        model = self.model
        xc = blockSize[0]
        yc = blockSize[1]

        logger.debug("size: %s" % (str(xc)))
        logger.debug("x %s" % (str(yc)))

        haloSize = model.base.getHaloSize()
        if haloSize > 1:
            raise AttributeError("Halosize>1 is not supported yet")
        
        logger.info("1 fill center funcs")
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]
        
        '''    
        for center_data in functionMap["center"]:
             funcIdx, xfrom, xto, yfrom, yto = center_data
             xfromIdx, xtoIdx = getXrange(block, xfrom, xto)
             yfromIdx, ytoIdx = getYrange(block, yfrom, yto)
        '''

        for center_data in functionMap["center"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx = center_data
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        logger.info("fill side 0 funcs")
        '''
        for side_data in functionMap["side0"]:
            funcIdx, xfrom, xto, yfrom, yto = side_data
            yfromIdx, ytoIdx = self.dmodel.getYrange(block, yfrom, yto)
        '''
        for side_data in functionMap["side0"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx = side_data
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        logger.info("fill side 1 funcs")
        '''
        for side_data in functionMap["side1"]:
            funcIdx, xfrom, xto, yfrom, yto = side_data
            yfromIdx, ytoIdx = self.dmodel.getYrange(block, yfrom, yto)
        '''
        for side_data in functionMap["side1"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx = side_data
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        logger.info("fill side 2 funcs")
        '''
        for side_data in functionMap["side2"]:
            funcIdx, xfrom, xto, yfrom, yto = side_data
            xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        '''
        for side_data in functionMap["side2"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx = side_data
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        logger.info("fill side 3 funcs")
        '''
        for side_data in functionMap["side3"]:
            funcIdx, xfrom, xto, yfrom, yto = side_data
            xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        '''
        for side_data in functionMap["side3"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx = side_data
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx

        logger.info("2 fill edges")
        funcArr[0, 0] = functionMap["v02"]
        funcArr[0, xc-1] = functionMap["v12"]
        funcArr[yc-1, 0] = functionMap["v03"]
        funcArr[yc-1, xc-1] = functionMap["v13"]
        
