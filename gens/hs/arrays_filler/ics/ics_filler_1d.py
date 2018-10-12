import numpy as np
import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.ics_filler_1d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_filler_1d')
logger.setLevel(level=log_level)
'''

bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def interconnect1dFill(self, icIdx):
        
        '''Fill arrays according to specification
        (see filler_main.py)'''

        model = self.net.model
        grid = model.grid

        ic = model.interconnects[icIdx]
        icDim = model.blocks[ic.block1].dimension - 1

        block1 = model.blocks[ic.block1]
        block2 = model.blocks[ic.block2]
        [b1xc, b1yc, b1zc] = (block1
                              .getCellCount(grid.gridStepX, grid.gridStepY,
                                            grid.gridStepZ))

        [b2xc, b2yc, b2zc] = (block2
                              .getCellCount(grid.gridStepX, grid.gridStepY,
                                            grid.gridStepZ))
        [b1xoff, b1yoff, b1zoff] = (block1
                                    .getCellOffset(grid.gridStepX,
                                                   grid.gridStepY,
                                                   grid.gridStepZ))
        [b2xoff, b2yoff, b2zoff] = (block2
                                    .getCellOffset(grid.gridStepX,
                                                   grid.gridStepY,
                                                   grid.gridStepZ))
        print("Filling interconnect", icIdx, ": block1 off:",
              b1xoff, b1yoff, b1zoff, "; block2 off:",
              b2xoff, b2yoff, b2zoff)
        
        if (ic.block1Side == 0) or (ic.block1Side == 1):
            # x=const connection
            if b1yoff < b2yoff:
                b1off = b2yoff - b1yoff
                b2off = 0
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1off = 0
                b2off = b1yoff - b2yoff
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
        else:
            # y=const connection
            if b1xoff < b2xoff:
                b1off = b2xoff - b1xoff
                b2off = 0
                icLen = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1off = 0
                b2off = b1xoff - b2xoff
                icLen = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff

        print("Saving interconnect", icIdx, "part 1")
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = icLen
        icPropArr1[2] = ic.block1  # source block
        icPropArr1[3] = ic.block2  # distination block
        icPropArr1[4] = ic.block1Side  # source side
        icPropArr1[5] = ic.block2Side  # distination side
        icPropArr1[6] = b1off  # source offset
        icPropArr1[7] = b2off  # destination offset
        self.icList.append(icPropArr1)
        print(icPropArr1)

        print("Saving interconnect", icIdx, "part 2")
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = icLen
        icPropArr2[2] = ic.block2  # source block
        icPropArr2[3] = ic.block1  # distination block
        icPropArr2[4] = ic.block2Side  # source side
        icPropArr2[5] = ic.block1Side  # distination side
        icPropArr2[6] = b2off  # source offset
        icPropArr2[7] = b1off  # destination offset
        self.icList.append(icPropArr2)
        print(icPropArr2)
