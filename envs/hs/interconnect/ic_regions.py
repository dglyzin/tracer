from math_space.common.someFuncs import determineCISC2D
from math_space.common.someFuncs import getRangesInClosedInterval
from math_space.common.someClasses import Params
from math_space.interval.interval_main import Interval

from copy import deepcopy as copy

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('ic_main.ic_regions')

# if using directly uncoment that:

'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ic_main')
logger.setLevel(level=log_level)
'''


class icRegions(dict):

    def __init__(self, net):
        self.net = net

        # storage for regions:
        self[1] = Params()
        self[2] = Params()
        
    def make_regions(self, reset_firstIdx=False):

        '''Create region for each block in current inteconnect.
        See ``make_region`` description for more.

        Input:
        
        -``reset_firstIdx`` -- if true rewrite global firstIndex
        (stored in model and used for region indexes in ics array.)'''

        if self.net.model.dimension == 1:
            # in case of block dimension 1 (or
            # ic dimension 0) there is no regions.
            return()

        if reset_firstIdx:
            self.net.model._ics_firstIndex = 0
        else:
            try:
                self.net.model._ics_firstIndex
            except AttributeError:
                self.net.model._ics_firstIndex = 0
                logger.debug("model firstIndex reseted")

        # firstIndex = self.net.model._ics_firstIndex

        block1 = self.net.model.blocks[self.net.block1]
        block1Side = self.net.block1Side

        block2 = self.net.model.blocks[self.net.block2]
        block2Side = self.net.block2Side

        # it also work for closed block case:
        self[1] = self.make_region(block1Side, block1, block2, 1)
        self[2] = self.make_region(block2Side, block2, block1, 2)
        
    def make_region(self, mainBlockSide, mainBlock, secondBlock,
                    region_num):
        
        '''Make some data for each block in ic.
        
        First it's find side and intervals, in which
        ic to be used. For interval it used ``Interval``
        object with bound and equation numbers set to
        ``None`` (i.e. ``name={'b': None, 'e': None}``).
        
        Also It create ranges that is rectangle
        ``[xfrom, xto, yfrom, yto]`` where all in cell sizes.

        interval, xfrom, xto, yfrom, yto, lenOfConnection,
        beforeStartLen, ranges is all inteconnect data,
        relative to mainBlock.
        
        It also add first index of current inteconnect
        for created region and increase it global value
        (stored in ``model._ics_firstIndex``)

        It create ``secondIndex`` which is index to be
        used by ``mainBlock`` in order to get according
        ``ics`` data for according side coordinate.

        (ex (what ``secondIndex`` used for):
        
           secondIndex: ic[firstIndex][secondIndex] for mainBlock
              where ic is inteconnects array,
                 firstIndex is index of ic mainBlock and secondBlock
                 secondIndex according mainBlock side (see ex below))

        (ex (how ``secondIndex`` created for side 2 or 3):

           secondIndex = idxX - to_cell(lenBSBSSC)
              where lenBSBSSC is len between start of block side
                 and start of connection)

        Tests:

        >>> from envs.hs.model.model_main import ModelNet as Model
        >>> m = Model()
        >>> m.io.loadFromFile('problems/2dTests/tests_2d_two_blocks0')
        >>> ic = m.interconnects[0]
        >>> icr = ic.regions[1]
        >>> icr.ranges
        [0, 301, 0, 1]

        >>> icr = ic.regions[2]
        >>> icr.ranges
        [150, 451, 700, 701]
        '''

        grid = self.net.model.grid
        den = mainBlock.defaultEquation

        if mainBlockSide == 0:

            xfrom = 0  # mainBlock.size.offsetX
            xto = 0  # mainBlock.size.offsetX
            yfrom = (max([secondBlock.size.offsetY, mainBlock.size.offsetY])
                     - mainBlock.size.offsetY)
            yto = (min([mainBlock.size.offsetY + mainBlock.size.sizeY,
                        secondBlock.size.offsetY + secondBlock.size.sizeY])
                   - mainBlock.size.offsetY)
            interval = Interval([yfrom, yto])

            beforeStartLen = yfrom
            lenOfConnection = yto - yfrom
            sideIndex = 'idxY'
            stepAlongSide = grid.gridStepY

        elif mainBlockSide == 1:

            xfrom = mainBlock.size.sizeX  # + mainBlock.size.offsetX
            xto = mainBlock.size.sizeX  # + mainBlock.size.offsetX
            yfrom = (max([secondBlock.size.offsetY, mainBlock.size.offsetY])
                     - mainBlock.size.offsetY)
            yto = (min([mainBlock.size.offsetY + mainBlock.size.sizeY,
                        secondBlock.size.offsetY + secondBlock.size.sizeY])
                   - mainBlock.size.offsetY)
            interval = Interval([yfrom, yto])

            beforeStartLen = yfrom
            lenOfConnection = yto - yfrom
            sideIndex = 'idxY'
            stepAlongSide = grid.gridStepY

        elif mainBlockSide == 2:

            xfrom = (max([mainBlock.size.offsetX, secondBlock.size.offsetX])
                     - mainBlock.size.offsetX)
            xto = (min([mainBlock.size.offsetX + mainBlock.size.sizeX,
                        secondBlock.size.offsetX + secondBlock.size.sizeX])
                   - mainBlock.size.offsetX)
            yfrom = 0  # mainBlock.size.offsetY
            yto = 0  # mainBlock.size.offsetY
            interval = Interval([xfrom, xto])

            beforeStartLen = xfrom
            lenOfConnection = xto - xfrom
            sideIndex = 'idxX'
            stepAlongSide = grid.gridStepX

        else:

            xfrom = (max([mainBlock.size.offsetX, secondBlock.size.offsetX])
                     - mainBlock.size.offsetX)
            xto = (min([mainBlock.size.offsetX + mainBlock.size.sizeX,
                        secondBlock.size.offsetX + secondBlock.size.sizeX])
                   - mainBlock.size.offsetX)
            yfrom = mainBlock.size.sizeY  # + mainBlock.size.offsetY
            yto = mainBlock.size.sizeY  # + mainBlock.size.offsetY
            interval = Interval([xfrom, xto])

            beforeStartLen = xfrom
            lenOfConnection = xto - xfrom
            sideIndex = 'idxX'
            stepAlongSide = grid.gridStepX

        self.net.model._ics_firstIndex += 1

        # FOR collect data:
        out = Params()

        out.firstIndex = self.net.model._ics_firstIndex
        
        out.side_num = mainBlockSide
        # out.stepAlongSide = stepAlongSide
        # out.beforeStartLen = beforeStartLen
        
        # map: block side index -> second index of ic
        # (ex: idxX -> secondIndex where secondIndex: ic[][secondIndex]):
        startCellIndex = determineCISC2D(beforeStartLen, stepAlongSide)
        out.secondIndex = ('(' + sideIndex + ' - ' + str(startCellIndex)
                           + ') * Block' + str(mainBlock.blockNumber)
                           + 'CELLSIZE')

        out.icLen = lenOfConnection

        side = mainBlock.sides[mainBlockSide]
        logger.debug("side.interval:")
        logger.debug(side.interval)
        logger.debug("icr.interval:")
        logger.debug(interval)

        # add default name:
        interval.name = {'b': None, 'e': den,
                         'i': (lambda _self=self, _region_num=region_num:
                               _self[_region_num])}
        # region_num - is global name
        # while _region_num is local name in lambda
        # that used because otherwise all regions
        # would have same region_num.
        
        # split at equation and bounds regions:
        out.intervals = interval.split_all([copy(interval)
                                            for interval in side.interval], [])

        # add ic info into block.side:
        side.interval = sum([i.split_all(out.intervals, [])
                             for i in side.interval], [])
        out.xfrom = xfrom
        out.xto = xto
        out.yfrom = yfrom
        out.yto = yto

        ranges = getRangesInClosedInterval([xfrom, xto, grid.gridStepX],
                                           [yfrom, yto, grid.gridStepY])
        out.ranges = ranges

        out.blockNumber = mainBlock.blockNumber
        out.ic = self.net
        out.ic_regions = self
        # END FOR

        return(out)
