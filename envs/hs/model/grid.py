from math_space.common.someFuncs import getRangesInClosedInterval


class Grid():
    def getXrange(self, xfrom, xto):
        # xfrom -= block.offsetX
        # xto -= block.offsetX
        fromIdx, toIdx = getRangesInClosedInterval([xfrom, xto, self.gridStepX])
        # [xc, _, _ ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == xc: toIdx = xc-1
        return fromIdx, toIdx
    
    def getYrange(self, block, yfrom, yto):
        # yfrom -= block.offsetY
        # yto -= block.offsetY
        fromIdx, toIdx = getRangesInClosedInterval([yfrom, yto, self.gridStepY])
        # [_, yc, _ ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == yc: toIdx = yc-1
        return fromIdx, toIdx
    
    def getZrange(self, block, zfrom, zto):
        # zfrom -= block.offsetZ
        # zto -= block.offsetZ
        fromIdx, toIdx = getRangesInClosedInterval([zfrom, zto, self.gridStepZ])
        # [_, _, zc ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        # if fromIdx == 0: fromIdx = 1
        # if toIdx == zc: toIdx = zc-1
        return fromIdx, toIdx

    def __repr__(self):
        out = ""
        attrs = self.__dict__
        for key_atr in attrs.keys():
            out += key_atr + ":" + str(attrs[key_atr]) + "\n"
        return(out)
