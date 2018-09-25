from gens.hs.env.bounds.common.bounds_common_dom import GenBaseDomCommon
from gens.hs.env.base.base_common import Params


class GenDomD2(GenBaseDomCommon):

    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_dom_bounds(self, model):
        dim = model.dimension

        self._set_params_for_vertex()
        self.set_params_for_dom_common(dim)

    # bounds vertex
    def _set_params_for_vertex(self):
        for bound in self.bounds_vertex:
            # for compatibility with old version of saveDomain
            if bound.sides in [[2, 1], [3, 0]]:
                vertexName = 'v%d%d' % (bound.sides[1], bound.sides[0])
            else:
                vertexName = 'v%d%d' % (bound.sides[0], bound.sides[1])

            eq_num = (self.namesAndNumbers[bound.blockNumber]
                      .index(bound.funcName))
            (self.functionMaps[bound.blockNumber]
             .update({vertexName: eq_num}))

    def _get_idx(self, model, bound):
        '''
        DESCRIPTION:

        Get idx for bound.side. For 2d.

        RETURN:

        for 2d
        [equation number, xfrom, xto, yfrom, yto]
        '''
        eq_num = self.namesAndNumbers[bound.blockNumber].index(bound.funcName)

        block = model.blocks[bound.blockNumber]
        if bound.side == 0:
            xfrom = 0
            xto = 0
            yfrom = bound.region[0]
            yto = bound.region[1]

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because xfrom == xto == 0
            # and Im(xfrom) == 0 and Im(xto) == 1
            # make Im(xto) = 0 (==Im(xfrom))
            # ranges[1] = ranges[0]

        elif(bound.side == 1):
            xfrom = block.sizeX
            xto = block.sizeX
            yfrom = bound.region[0]
            yto = bound.region[1]

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because xfrom == xto == sizeX
            # and Im(xfrom) == Im(sizeX) and Im(xto) == Im(sizeX)+1
            # make Im(xfrom) = Im(sizeX)+1 (==Im(xto))
            # ranges[0] = ranges[1]

        elif(bound.side == 2):
            xfrom = bound.region[0]
            xto = bound.region[1]
            yfrom = 0
            yto = 0

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because yfrom == yto == 0
            # and Im(yfrom) == 0 and Im(yto) == 1
            # make Im(yto) = 0 (==Im(yfrom))
            # ranges[3] = ranges[2]

        elif(bound.side == 3):
            xfrom = bound.region[0]
            xto = bound.region[1]
            yfrom = block.sizeY
            yto = block.sizeY

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because yfrom == yto == sizeY
            # and Im(yfrom) == Im(sizeY) and Im(yto) == Im(sizeY)+1
            # make Im(yfrom) = Im(sizeY)+1 (==Im(yto))
            # ranges[2] = ranges[3]

        idx = [eq_num] + ranges
        return(idx)
