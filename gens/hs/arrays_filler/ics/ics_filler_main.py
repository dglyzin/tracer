from gens.hs.arrays_filler.ics.ics_filler_0d import Filler as FillerD0
from gens.hs.arrays_filler.ics.ics_filler_1d import Filler as FillerD1
# from gens.hs.arrays_filler.ics.ics_filler_2d import Filler as FillerD2
from gens.hs.arrays_filler.ics.ics_filler_plot import Plotter

import numpy as np
from functools import reduce
from collections import OrderedDict

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.ics_filler_main')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_filler_main')
logger.setLevel(level=log_level)
'''

devType = {"cpu": 0, "gpu": 1}


class Filler():
    
    def __init__(self, model):
        self.model = model
        
        self.d0 = FillerD0(self)
        self.d1 = FillerD1(self)
        # self.d2 = FillerD2(self)

        self.plotter = Plotter(self)

    def fillBinaryInterconnects(self):

        '''
        Fill::

            ``self.icCount``
            ``self.icCountArr``
            ``self.icList``
        '''

        self.icCount = len(self.model.interconnects)
        self.icCountArr = np.zeros(1, dtype=np.int32)
        self.icCountArr[0] = self.icCount*2
        logger.info("saving %s ics" % (str(self.icCountArr[0])))

        self.icList = []
        for icIdx in range(self.icCount):
            # ic = self.model.interconnects[icIdx]
            # icDim = self.model.blocks[ic.block1].dimension - 1
            icDim = self.model.dimension - 1
            if icDim == 0:
                self.d0.interconnect0dFill(icIdx)
            elif icDim == 1:
                self.d1.interconnect1dFill(icIdx)
            elif icDim == 2:
                self.d2.interconnect2dFill(icIdx)

        self.blocks_ics = self.show_ics_for_each_block(icDim)

    def show_ics_for_each_block(self, icDim):
        
        '''Show ics array for each block (used in .cpp interconnects
        functions)
        At ``hs`` it equivalent ``externalBorder`` for each block.
        
        Example:

        (see heat_block_0_ics_other)

        for icList
           icDim  icLen  source block  dist_block  source side  dist side  \
        0      1    101             0           1            0          1   
        1      1    101             1           0            1          0   
        2      1    101             0           1            1          0   
        3      1    101             1           0            0          1   

           source offset  dist offset  
        0              0            0  
        1              0            0  
        2              0            0  
        3              0            0  

        blocks_ics will be:
                                         0                          1
        dist_b1  src_b0.src_s0 for dist_s1  src_b0.src_s1 for dist_s0
        dist_b0  src_b1.src_s1 for dist_s0  src_b1.src_s0 for dist_s1

        '''

        def succ(acc, ic):
            
            if icDim == 0:
                source_block = ic[1]
                dist_block = ic[2]
                source_side = ic[3]
                dist_side = ic[4]
            elif icDim == 1:
                source_block = ic[2]
                dist_block = ic[3]
                source_side = ic[4]
                dist_side = ic[5]

            data = ("src_b%s.src_s%s for dist_s%s"
                    % (str(source_block), str(source_side),
                       str(dist_side)))

            if dist_block not in acc:
                acc[dist_block] = [data]
            else:
                acc[dist_block].append(data)
            return(acc)

        blocks_ics = reduce(succ, self.icList, OrderedDict())
        
        return(blocks_ics)

    def save_bin(self, domfile):

        self.icCountArr.tofile(domfile)
        for icArr in self.icList:
            icArr.tofile(domfile)
