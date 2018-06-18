from math_space.common.someFuncs import getRangesInClosedInterval


class GridDom():
    def __init__(self, net):
        self.net = net

    def get_ranges(self, eRegion):
        model = self.net.model
        dim = model.dimension

        if dim == 1:
            ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto,
                                                model.grid.gridStepX])
        elif dim == 2:
            ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto,
                                                model.grid.gridStepX],
                                               [eRegion.yfrom, eRegion.yto,
                                                model.grid.gridStepY])
        return(ranges)
