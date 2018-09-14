import numpy as np
from pandas import DataFrame


class icDom():

    def __init__(self, net):
        self.net = net
    
    def __repr__(self):
        out = ""
        try:
            out += "b1xc: %s \n" % str(self.b1xc)
            out += "b1yc: %s \n" % str(self.b1yc)
            out += "b1zc: %s \n" % str(self.b1zc)
            out += "\n"

            out += "b1xoff: %s \n" % str(self.b1xoff)
            out += "b1yoff: %s \n" % str(self.b1yoff)
            out += "b1zoff: %s \n" % str(self.b1zoff)
            out += "b1offN: %s \n" % str(self.b1offN)
            out += "b1offM: %s \n" % str(self.b1offM)
            out += "\n"

            out += "b2xc: %s \n" % str(self.b2xc)
            out += "b2yc: %s \n" % str(self.b2yc)
            out += "b2zc: %s \n" % str(self.b2zc)
            out += "\n"

            out += "b2xoff: %s \n" % str(self.b2xoff)
            out += "b2yoff: %s \n" % str(self.b2yoff)
            out += "b2zoff: %s \n" % str(self.b2zoff)
            out += "b2offN: %s \n" % str(self.b2offN)
            out += "b2offM: %s \n" % str(self.b2offM)
            out += "\n"

            out += "icLenN: %s \n" % str(self.icLenN)
            out += "icLenM: %s \n" % str(self.icLenM)
            out += "\n"

            out += "\n"
            index = ["icArr1:"]
            columns = ["dim", "icLenM", "icLenN",
                       "block1", "block2", "block1Side", "block2Side",
                       "b1offM", "b1offN", "b2offM", "b2offN"]
            out += str(DataFrame([self.icArr1], columns=columns,
                                 index=index))
            out += "\n \n"
            index = ["icArr2:"]
            columns = ["dim", "icLenM", "icLenN",
                       "block2", "block1", "block2Side", "block1Side",
                       "b2offM", "b2offN", "b1offM", "b1offN"]
            
            out += str(DataFrame([self.icArr1], columns=columns,
                                 index=index))
            out += "\n"

        except AttributeError:
            raise(BaseException("use ic_2d_fill first"))
        return(out)

    def ic_2d_fill(self):
        
        '''Create interconnect data for dom file (icArr1, icArr2).
        Add interconnect parameters to ``self``:
        ``N, M`` - axis of interconnect (ex: ``M = Y, M = Z``)
        ``icLenM, icLenN`` - count of cells in axis N, M.
        ``b2xoff`` - begining of interconnect in block 2
        
        '''
        
        ic = self.net
        icDim = ic.model.blocks[ic.block1].size.dimension - 1

        block1 = ic.model.blocks[ic.block1]
        block2 = ic.model.blocks[ic.block2]

        grid = ic.model.grid

        block1_size = block1.size
        block2_size = block2.size

        [b1xc, b1yc, b1zc] = block1_size.getCellCount(grid.gridStepX,
                                                      grid.gridStepY,
                                                      grid.gridStepZ)
        [b2xc, b2yc, b2zc] = block2_size.getCellCount(grid.gridStepX,
                                                      grid.gridStepY,
                                                      grid.gridStepZ)
        [b1xoff, b1yoff, b1zoff] = block1_size.getCellOffset(grid.gridStepX,
                                                             grid.gridStepY,
                                                             grid.gridStepZ)
        [b2xoff, b2yoff, b2zoff] = block2_size.getCellOffset(grid.gridStepX,
                                                             grid.gridStepY,
                                                             grid.gridStepZ)
        if (ic.block1Side == 0) or (ic.block1Side == 1):
            # x = const connection
            print("N = Y")
            
            if b1yoff < b2yoff:
                b1offN = b2yoff - b1yoff
                b2offN = 0
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offN = 0
                b2offN = b1yoff - b2yoff
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
            print("M = Z")
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        elif (ic.block1Side == 2) or (ic.block1Side == 3):
            # y = const connection
            print("N = X")
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            print("M = Z")
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        else:
            # z = const connection
            print("N = X")
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            print("M = Y")
            if b1yoff < b2yoff:
                b1offM = b2yoff - b1yoff
                b2offM = 0
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offM = 0
                b2offM = b1yoff - b2yoff
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
        
        print("b1xc: %s" % (str(b1xc)))
        print("b1yc: %s" % (str(b1yc)))
                
        print("b1xoff: %s" % (str(b1xoff)))
        print("b1yoff: %s" % (str(b1yoff)))

        print("b1offN: %s" % (str(b1offN)))
        print("b1offM: %s" % (str(b1offM)))

        print("icLenN: %s" % (str(icLenN)))
        print("icLenM: %s" % (str(icLenM)))

        print("b2xc: %s" % (str(b2xc)))
        print("b2yc: %s" % (str(b2yc)))
                
        print("b2xoff: %s" % (str(b2xoff)))
        print("b2yoff: %s" % (str(b2yoff)))

        print("b2offN: %s" % (str(b2offN)))
        print("b2offM: %s" % (str(b2offM)))

        self.b1xc = b1xc
        self.b1yc = b1yc
        self.b1zc = b1zc

        self.b1xoff = b1xoff
        self.b1yoff = b1yoff
        self.b1zoff = b1zoff
        self.b1offN = b1offN
        self.b1offM = b1offM

        self.b2xc = b2xc
        self.b2yc = b2yc
        self.b2zc = b2zc

        self.b2xoff = b2xoff
        self.b2yoff = b2yoff
        self.b2zoff = b2zoff
        self.b2offN = b2offN
        self.b2offM = b2offM
        
        self.icLenN = icLenN
        self.icLenM = icLenM

        icPropArr1 = np.zeros(11, dtype=np.int32)  # 5+3*icDim
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
        
        self.icArr1 = icPropArr1

        icPropArr2 = np.zeros(11, dtype=np.int32)  # 5+3*icDim
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
        self.icArr2 = icPropArr2

