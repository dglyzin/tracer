import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.ics_filler_2d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_filler_2d')
logger.setLevel(level=log_level)
'''

bdict = {"dirichlet": 0, "neumann": 1}


class Filler():
    def __init__(self, net):
        self.net = net

    def interconnect2dFill(self, icIdx):
        ic = self.dmodel.interconnects[icIdx]
        icDim = self.dmodel.blocks[ic.block1].dimension - 1

        block1 = self.dmodel.blocks[ic.block1]
        block2 = self.dmodel.blocks[ic.block2]
        [b1xc, b1yc, b1zc] = (block1
                              .getCellCount(self.dmodel.gridStepX,
                                            self.dmodel.gridStepY,
                                            self.dmodel.gridStepZ))
        [b2xc, b2yc, b2zc] = (block2
                              .getCellCount(self.dmodel.gridStepX,
                                            self.dmodel.gridStepY,
                                            self.dmodel.gridStepZ))
        [b1xoff, b1yoff, b1zoff] = (block1
                                    .getCellOffset(self.dmodel.gridStepX,
                                                   self.dmodel.gridStepY,
                                                   self.dmodel.gridStepZ))
        [b2xoff, b2yoff, b2zoff] = (block2
                                    .getCellOffset(self.dmodel.gridStepX,
                                                   self.dmodel.gridStepY,
                                                   self.dmodel.gridStepZ))
        
        print("Filling interconnect", icIdx,
              ": block1 off:", b1xoff, b1yoff, b1zoff,
              "; block2 off:", b2xoff, b2yoff, b2zoff)
        
        if (ic.block1Side == 0) or (ic.block1Side == 1):
            #x=const connection
            #Y=N
            if b1yoff < b2yoff:
                b1offN = b2yoff - b1yoff
                b2offN = 0
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offN = 0
                b2offN = b1yoff - b2yoff
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
            #Z=M
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        elif (ic.block1Side == 2) or (ic.block1Side == 3):
            #y=const connection
            #X=N
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            #Z=M
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        else:
            #z=const connection
            #X=N
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            #Y=M
            if b1yoff < b2yoff:
                b1offM = b2yoff - b1yoff
                b2offM = 0
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offM = 0
                b2offM = b1yoff - b2yoff
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
            
        print("Saving interconnect", icIdx, "part 1")
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = icLenM
        icPropArr1[2] = icLenN
        icPropArr1[3] = ic.block1
        icPropArr1[4] = ic.block2
        icPropArr1[5] = ic.block1Side
        icPropArr1[6] = ic.block2Side
        icPropArr1[7] = b1offM
        icPropArr1[8] = b1offN
        icPropArr1[9] = b2offM
        icPropArr1[10] = b2offN
        
        self.icList.append(icPropArr1)
        print(icPropArr1)

        print("Saving interconnect", icIdx, "part 2")
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = icLenM
        icPropArr2[2] = icLenN
        icPropArr2[3] = ic.block2
        icPropArr2[4] = ic.block1
        icPropArr2[5] = ic.block2Side
        icPropArr2[6] = ic.block1Side
        icPropArr2[7] = b2offM
        icPropArr2[8] = b2offN
        icPropArr2[9] = b1offM
        icPropArr2[10] = b1offN
        self.icList.append(icPropArr2)
        print(icPropArr2)
