from gens.hs.common.init_funcs_nums import InitFuncsNums

import numpy as np

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('filler_main.blocks_filler_1d')

# if using directly uncoment that:

# create logger
'''
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('blocks_filler_1d')
logger.setLevel(level=log_level)
'''

bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def fill1dInitFuncs(self, funcArr, block, blockSize):
        logger.info("Filling 1d initial function array.")
        xc = blockSize[0]
        
        ifn = InitFuncsNums(self.net.model, block)

        # TODO: to common:
        logger.info("1 fill default conditions")
        '''
        usedInitNums = [block.defaultInitial]
        initFuncNum = usedInitNums.index(block.defaultInitial)
        funcArr[:] = initFuncNum
        '''
        initFuncNum = ifn.get_default_initial(block.defaultInitial)
        funcArr[:] = initFuncNum

        logger.info("2 fill user-defined conditions:")
        
        '''
        logger.info("2.1 collect user-defines initial conditions")
        # that are used in this block
        for initReg in block.initialRegions:
            if not (initReg.initialNumber in usedInitNums):
                usedInitNums.append(initReg.initialNumber)
        '''
        # END OF TODO

        # logger.info("2.2 fill them")
        for iRegion in block.initialRegions:
            initFuncNum = ifn.get_initial_regions(iRegion.initialNumber)
            # initFuncNum = usedInitNums.index(initReg.initialNumber)
            getXrange = self.net.model.grid.base.getXrange
            xstart, xend = getXrange(iRegion.xfrom, iRegion.xto)
            funcArr[xstart:xend] = initFuncNum

        logger.info("3 overwrite with values that come from Dirichlet bounds")
        logger.info("3.1 collect dirichlet bound numbers"
                    + "that are used in this block")
        # TODO: to common
        '''
        usedIndices = len(usedInitNums)
        usedDirBoundNums = []
        for side_num in block.boundRegions:
            for bound in block.boundRegions[side_num]:
                boundNumber = bound.boundNumber
                if not (boundNumber in usedDirBoundNums):
                    bound_btype = self.net.model.bounds[boundNumber].btype
                    if (bound_btype == bdict["dirichlet"]):
                        usedDirBoundNums.append(boundNumber)

        usedDirBoundNums.sort()
        # END OF TODO
        logger.debug("Used Dirichlet bound nums:")
        logger.debug(usedDirBoundNums)
        '''

        logger.info("3.2 fill them")
        for side_num in block.boundRegions:
            for bound in block.boundRegions[side_num]:
                boundNumber = bound.boundNumber
                bound_btype = self.net.model.bounds[boundNumber].btype
                if (bound_btype == bdict["dirichlet"]):

                    # for initFuncArray indexes
                    # factorization dirichlet/undirichlet:
                    initFuncNum = ifn.get_dirichlet_bound_regions(boundNumber)
                    # initFuncNum = (usedIndices
                    #                + usedDirBoundNums.index(boundNumber))
                    # legacy form
                    # block.boundRegions[boundNumber].side_num
                    if side_num == 0:
                        idxX = 0
                    elif side_num == 1:
                        idxX = xc - 1
                    funcArr[idxX] = initFuncNum

    def fill1dCompFuncs(self, funcArr, block, functionMap, blockSize):
        logger.info("Filling 1d main function array.")

        logger.debug("Function mapping for this block:")
        logger.debug(functionMap)

        xc = blockSize[0]
        logger.debug("size:")
        logger.debug(xc)

        haloSize = self.net.model.base.getHaloSize()
        if haloSize > 1:
            raise AttributeError("Halosize>1 is not supported yet")

        logger.info("1 fill center funcs")
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]
            
        # for [funcIdx, xfrom, xto] in functionMap["center"]:
        #    xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        for [funcIdx, xfromIdx, xtoIdx] in functionMap["center"]:
            funcArr[xfromIdx:xtoIdx] = funcIdx
        
        logger.info("2 fill edges")
        funcArr[0] = functionMap["side0"]
        funcArr[xc-1] = functionMap["side1"]
