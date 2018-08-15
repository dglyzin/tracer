import numpy as np
from pandas import DataFrame
from collections import OrderedDict

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.filler_plot')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('filler_plot')
logger.setLevel(level=log_level)
'''


class Filler():
    def __init__(self, model):
        self.model = model
        
    def fillBinaryPlots(self):
        '''
        Fill
        self.plotAndResCountArr
        self.plotAndResPeriodsArr
        '''
        plotCount = len(self.model.plots)
        resCount = len(self.model.results)
        self.plotAndResCountArr = np.zeros(1, dtype=np.int32)
        self.plotAndResCountArr[0] = plotCount + resCount
        self.plotAndResPeriodsArr = np.zeros(plotCount + resCount,
                                             dtype=np.float64)
        for plotIdx in range(plotCount):
            period = self.model.plots[plotIdx]["Period"]
            self.plotAndResPeriodsArr[plotIdx] = period

        for resIdx in range(resCount):
            period = self.model.results[resIdx]["Period"]
            self.plotAndResPeriodsArr[plotCount + resIdx] = period
        
    def show(self, gout={}):
        out = OrderedDict()
        out['plotAndResCountArr'] = {
            'array': self.plotAndResCountArr,
            'frame': DataFrame([self.plotAndResCountArr])}

        out['plotAndResPeriodsArr'] = {
            'array': self.plotAndResPeriodsArr,
            'frame': DataFrame([self.plotAndResPeriodsArr])}

        gout['plotAndRes'] = out
        return(gout)

    def save_bin(self, domfile):
        
        self.plotAndResCountArr.tofile(domfile)
        self.plotAndResPeriodsArr.tofile(domfile)
        logger.debug("plot periods: %s" % (str(self.plotAndResCountArr)))
        logger.debug("result periods: %s" % (str(self.plotAndResPeriodsArr)))
