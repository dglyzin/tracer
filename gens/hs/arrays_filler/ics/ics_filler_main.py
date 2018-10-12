from gens.hs.arrays_filler.ics.ics_filler_0d import Filler as FillerD0
from gens.hs.arrays_filler.ics.ics_filler_1d import Filler as FillerD1
# from gens.hs.arrays_filler.ics.ics_filler_2d import Filler as FillerD2
from gens.hs.arrays_filler.ics.ics_filler_plot import Plotter

import numpy as np

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
            ic = self.model.interconnects[icIdx]
            # icDim = self.model.blocks[ic.block1].dimension - 1
            icDim = self.model.dimension - 1
            if icDim == 0:
                self.d0.interconnect0dFill(icIdx)
            elif icDim == 1:
                self.d1.interconnect1dFill(icIdx)
            elif icDim == 2:
                self.d2.interconnect2dFill(icIdx)

    def save_bin(self, domfile):

        self.icCountArr.tofile(domfile)
        for icArr in self.icList:
            icArr.tofile(domfile)
