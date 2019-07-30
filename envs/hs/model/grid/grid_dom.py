from spaces.some_space.someFuncs import getRangesInClosedInterval


class GridDom():
    def __init__(self, net):
        self.net = net

    def get_ranges(self, eRegion, dim=None):
        model = self.net.model

        if dim == 1 or model.dimension == 1:
            ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto,
                                                model.grid.gridStepX])
        elif dim == 2 or model.dimension == 2:
            ranges = getRangesInClosedInterval([eRegion.xfrom, eRegion.xto,
                                                model.grid.gridStepX],
                                               [eRegion.yfrom, eRegion.yto,
                                                model.grid.gridStepY])
        return(ranges)
