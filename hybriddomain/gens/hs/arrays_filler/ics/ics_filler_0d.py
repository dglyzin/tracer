import numpy as np

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.ics_filler_0d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_filler_0d')
logger.setLevel(level=log_level)
'''

bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def interconnect0dFill(self, icIdx):
        ic = self.net.model.interconnects[icIdx]
        icDim = 0
        logger.info("Saving interconnect %s part 1" % (str(icIdx)))
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = ic.block1
        icPropArr1[2] = ic.block2
        icPropArr1[3] = ic.block1Side
        icPropArr1[4] = ic.block2Side
        self.net.icList.append(icPropArr1)

        logger.info("Saving interconnect %s part 2" % (str(icIdx)))
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = ic.block2
        icPropArr2[2] = ic.block1
        icPropArr2[3] = ic.block2Side
        icPropArr2[4] = ic.block1Side
        self.net.icList.append(icPropArr2)

