from hybriddomain.spaces.some_space.someFuncs import getRangesInClosedInterval


class GridBase():
    def __init__(self, net):
        self.net = net

    def getXrange(self, xfrom, xto):
        # xfrom -= block.offsetX
        # xto -= block.offsetX
        fromIdx, toIdx = getRangesInClosedInterval([xfrom, xto,
                                                    self.net.gridStepX])
        # [xc, _, _ ] = block.getCellCount(self.gridStepX, self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == xc: toIdx = xc-1
        return fromIdx, toIdx
    
    def getYrange(self, yfrom, yto):
        # yfrom -= block.offsetY
        # yto -= block.offsetY
        fromIdx, toIdx = getRangesInClosedInterval([yfrom, yto,
                                                    self.net.gridStepY])
        # [_, yc, _ ] = block.getCellCount(self.net.gridStepX, self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == yc: toIdx = yc-1
        return fromIdx, toIdx
    
    def getZrange(self, zfrom, zto):
        # zfrom -= block.offsetZ
        # zto -= block.offsetZ
        fromIdx, toIdx = getRangesInClosedInterval([zfrom, zto,
                                                    self.net.gridStepZ])
        # [_, _, zc ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == zc: toIdx = zc-1
        return fromIdx, toIdx
