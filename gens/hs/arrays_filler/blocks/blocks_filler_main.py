from gens.hs.arrays_filler.blocks.blocks_filler_1d import Filler as FillerD1
from gens.hs.arrays_filler.blocks.blocks_filler_2d import Filler as FillerD2
from gens.hs.arrays_filler.blocks.blocks_filler_2d import Filler as FillerD3
from gens.hs.arrays_filler.blocks.blocks_filler_plot import Plotter
import numpy as np

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.blocks_filler_main')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('blocks_filler_main')
logger.setLevel(level=log_level)
'''

devType = {"cpu": 0, "gpu": 1}


class Filler():
    
    def __init__(self, model, functionMaps):
        self.model = model
        self.functionMaps = functionMaps

        self.d1 = FillerD1(self)
        self.d2 = FillerD2(self)
        self.d3 = FillerD3(self)

        self.plotter = Plotter(self)

    def fillBinaryBlocks(self):
        '''
        DESCRIPTION:
        Fill
        self.blockCountArr
        self.blockPropArrList
        self.blockInitFuncArrList
        self.blockCompFuncArrList
        '''
        logger.info("Welcome to Blocks Data filler")
        model = self.model
        functionMaps = self.functionMaps

        logger.debug("following is the function mapping")
        logger.debug(functionMaps)

        self.blockCount = len(model.blocks)
        self.blockCountArr = np.zeros(1, dtype=np.int32)
        self.blockCountArr[0] = self.blockCount
        self.blockPropArrList = []
        self.blockInitFuncArrList = []
        self.blockCompFuncArrList = []

        domainDim = model.dimension

        for blockIdx in range(self.blockCount):
            logger.debug("Saving block")
            logger.debug(blockIdx)
            block = model.blocks[blockIdx]

            logger.info("1. Fill block params")
            cellCountList = (block.size
                             .getCellCount(model.grid.gridStepX,
                                           model.grid.gridStepY,
                                           model.grid.gridStepZ))
            cellOffsetList = (block.size
                              .getCellOffset(model.grid.gridStepX,
                                             model.grid.gridStepY,
                                             model.grid.gridStepZ))

            cellCount = cellCountList[0]*cellCountList[1]*cellCountList[2]
            zc, yc, xc = cellCountList[2], cellCountList[1], cellCountList[0]

            blockPropArr = np.zeros(3+2*domainDim, dtype=np.int32)
            blockInitFuncArr = np.zeros(cellCount, dtype=np.int16)
            blockCompFuncArr = np.zeros(cellCount, dtype=np.int16)
            
            mapping = model.mapping[blockIdx]
            blockPropArr[0] = mapping["NodeIdx"]
            blockPropArr[1] = devType[mapping["DeviceType"]]
            blockPropArr[2] = mapping["DeviceIdx"]
            idx = 3
            blockPropArr[idx] = cellOffsetList[0]
            idx += 1
            if domainDim > 1:
                blockPropArr[idx] = cellOffsetList[1]
                idx += 1
            if domainDim > 2:
                blockPropArr[idx] = cellOffsetList[2]
                idx += 1
            blockPropArr[idx] = cellCountList[0]
            idx += 1
            if domainDim > 1:
                blockPropArr[idx] = cellCountList[1]
                idx += 1
            if domainDim > 2:
                blockPropArr[idx] = cellCountList[2]

            self.blockPropArrList.append(blockPropArr)
            logger.debug("blockPropArr")
            logger.debug(blockPropArr)

            logger.info("2. Fill block functions")
            if domainDim == 1:
                self.d1.fill1dInitFuncs(blockInitFuncArr, block, cellCountList)

                logger.debug("Initial function indices:")
                logger.debug(blockInitFuncArr)

                self.d1.fill1dCompFuncs(blockCompFuncArr, block,
                                        functionMaps[blockIdx], cellCountList)

                logger.debug("Computation function indices:")
                logger.debug(blockCompFuncArr)

            elif domainDim == 2:
                self.d2.fill2dInitFuncs(blockInitFuncArr.reshape([yc, xc]),
                                        block, cellCountList)
                
                logger.debug("Initial function indices:")
                logger.debug(blockInitFuncArr.reshape([yc, xc]))
                self.d2.fill2dCompFuncs(blockCompFuncArr.reshape([yc, xc]),
                                        block, functionMaps[blockIdx],
                                        cellCountList)
                logger.debug("Computation function indices:")
                logger.debug(blockCompFuncArr.reshape([yc, xc]))

            elif domainDim == 3:
                self.d3.fill3dInitFuncs(blockInitFuncArr.reshape([zc, yc, xc]),
                                        block, cellCountList)
                logger.debug("Initial function indices:")
                logger.debug(blockInitFuncArr.reshape([zc, yc, xc]))
                self.d3.fill3dCompFuncs(blockCompFuncArr.reshape([zc, yc, xc]),
                                        block, functionMaps[blockIdx],
                                        cellCountList)
                logger.debug("Computation function indices:")
                logger.debug(blockCompFuncArr.reshape([zc, yc, xc]))

            self.blockInitFuncArrList.append(blockInitFuncArr)
            self.blockCompFuncArrList.append(blockCompFuncArr)

    def save_bin(self, domfile):
        self.blockCountArr.tofile(domfile)
        for blockIdx in range(self.blockCount):
            self.blockPropArrList[blockIdx].tofile(domfile)
            self.blockInitFuncArrList[blockIdx].tofile(domfile)
            self.blockCompFuncArrList[blockIdx].tofile(domfile)

