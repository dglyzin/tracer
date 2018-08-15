import numpy as np

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.blocks_filler_3d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('blocks_filler_3d')
logger.setLevel(level=log_level)


bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def fill3dInitFuncs(self, funcArr, block, blockSize):
        logger.info("Filling 3d initial function array.")
        model = self.net.model
        getXrange = model.grid.base.getXrange
        getYrange = model.grid.base.getYrange
        getZrange = model.grid.base.getZrange

        xc = blockSize[0]
        yc = blockSize[1]
        zc = blockSize[2]

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
            zstart, zend = getYrange(block, initReg.zfrom, initReg.zto)
            funcArr[zstart:zend, ystart:yend, xstart:xend] = initFuncNum
        logger.debug("Used init nums:")
        logger.debug(usedInitNums)
        
        logger.info("3 overwrite with values that come from Dirichlet bounds")
        logger.info("3.1 collect dirichlet bound numbers")
        # that are used in this block
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
            bound_btype = model.bounds[boundReg.boundNumber].btype
            if (bound_btype == bdict["dirichlet"]):
                initFuncNum = (usedIndices
                               + usedDirBoundNums.index(boundReg.boundNumber))
                if boundReg.side == 0:
                    idxX = 0
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    zstart, zend = getZrange(block,
                                             boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, ystart:yend, idxX] = initFuncNum
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    zstart, zend = getZrange(block,
                                             boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, ystart:yend, idxX] = initFuncNum
                elif boundReg.side == 2:
                    idxY = 0
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    zstart, zend = getZrange(block,
                                             boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    zstart, zend = getZrange(block,
                                             boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 4:
                    idxZ = 0
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    funcArr[idxZ, ystart:yend, xstart:xend] = initFuncNum
                elif boundReg.side == 5:
                    idxZ = zc-1
                    xstart, xend = getXrange(block,
                                             boundReg.xfrom, boundReg.xto)
                    ystart, yend = getYrange(block,
                                             boundReg.yfrom, boundReg.yto)
                    funcArr[idxZ, ystart:yend, xstart:xend] = initFuncNum
        
    def fill3dCompFuncs(self, funcArr, block, functionMap, blockSize):
        logger.info("Filling 2d main function array.")
        model = self.net.model

        logger.debug("Function mapping for this block:")
        logger.debug(functionMap)
        xc = blockSize[0]
        yc = blockSize[1]
        zc = blockSize[2]
        logger.debug("size: %s x %s x %s" % (str(xc), str(yc), str(zc)))
        haloSize = model.base.getHaloSize()
        if haloSize > 1:
            raise AttributeError("Halosize>1 is not supported yet")

        logger.info("1.1 fill center default funcs")
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]
        logger.info("1.2 fill center funcs")
        for center_data in functionMap["center"]:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx = center_data
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx,
                    xfromIdx:xtoIdx] = funcIdx

        logger.info("2 fill 2d sides")
        sides = (functionMap["side0"] + functionMap["side1"]
                 + functionMap["side2"] + functionMap["side3"]
                 + functionMap["side4"] + functionMap["side5"])
        for side_data in sides:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx = side_data
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx,
                    xfromIdx:xtoIdx] = funcIdx
        logger.info("3 fill 1d edges")
        edges = (functionMap["edge02"] + functionMap["edge03"]
                 + functionMap["edge12"] + functionMap["edge13"]
                 + functionMap["edge04"] + functionMap["edge05"]
                 + functionMap["edge14"] + functionMap["edge15"]
                 + functionMap["edge24"] + functionMap["edge25"]
                 + functionMap["edge34"] + functionMap["edge35"])
        for edge_data in edges:
            funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx = edge_data
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx,
                    xfromIdx:xtoIdx] = funcIdx
        
        logger.info("4 fill point vertices")
        funcArr[0, 0, 0] = functionMap["v024"]
        funcArr[0, 0, xc-1] = functionMap["v124"]
        funcArr[0, yc-1, 0] = functionMap["v034"]
        funcArr[0, yc-1, xc-1] = functionMap["v134"]
        funcArr[zc-1, 0, 0] = functionMap["v025"]
        funcArr[zc-1, 0, xc-1] = functionMap["v125"]
        funcArr[zc-1, yc-1, 0] = functionMap["v035"]
        funcArr[zc-1, yc-1, xc-1] = functionMap["v135"]
