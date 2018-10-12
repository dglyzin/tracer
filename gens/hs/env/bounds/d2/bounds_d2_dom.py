from gens.hs.env.bounds.common.bounds_common_dom import GenBaseDomCommon
from math_space.common.someClasses import Params
from math_space.common.someFuncs import getRangesInClosedInterval


class GenDomD2(GenBaseDomCommon):

    def __init__(self, net):
        self.net = net
        self.params = Params()

    def set_params_for_dom_bounds(self, model,
                                  namesAndNumbers, functionMaps):
        '''
        DESCRIPTION:

        Add bounds data for 2d dom to ``functionMaps`` dict.

        Inputs:

        - ``self.net.params.bounds_edges`` -- from \
        ``self.net.common.set_params_for_bounds``

        - ``self.net.params.bounds_vertex`` -- from \
        ``self.net.common.set_params_for_bounds``

        - ``namesAndNumbers`` -- from \
           ``array_common.py: set_params_for_array``
           ``cent_common.py: set_params_for_centrals``
           ``ics_common.py: set_params_for_interconnects``
           ``bounds_common.py: set_params_for_bounds``

        ``namesAndNumbers`` is copy of ``pBoundFuncs`` of
        ``getBlockBoundFuncArray`` function.
        It contain func names at according position
        and used for getting right number of equations in domain file.

        '''
        dim = model.dimension

        self.params.namesAndNumbers = namesAndNumbers
        self.params.functionMaps = functionMaps

        self.set_params_for_vertex()
        self.set_params_for_dom_common(dim, model)

    # bounds vertex
    def set_params_for_vertex(self):
        for bound in self.net.params.bounds_vertex:
            # for compatibility with old version of saveDomain
            sides_nums = bound.sides_nums
            if sides_nums in [[2, 1], [3, 0]]:
                vertexName = 'v%d%d' % (sides_nums[1], sides_nums[0])
            else:
                vertexName = 'v%d%d' % (sides_nums[0], sides_nums[1])

            eq_num = (self.params.namesAndNumbers[bound.blockNumber]
                      .index(bound.funcName))
            (self.params.functionMaps[bound.blockNumber]
             .update({vertexName: eq_num}))

    def get_idx(self, model, bound):
        '''
        DESCRIPTION:

        Get idx for bound.side. For 2d.

        RETURN:

        for 2d
        [equation number, xfrom, xto, yfrom, yto]
        '''
        eq_num = (self.params
                  .namesAndNumbers[bound.blockNumber]
                  .index(bound.funcName))

        block = model.blocks[bound.blockNumber]
        if bound.side_num == 0:
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

        elif(bound.side_num == 1):
            xfrom = block.size.sizeX
            xto = block.size.sizeX
            yfrom = bound.region[0]
            yto = bound.region[1]

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because xfrom == xto == sizeX
            # and Im(xfrom) == Im(sizeX) and Im(xto) == Im(sizeX)+1
            # make Im(xfrom) = Im(sizeX)+1 (==Im(xto))
            # ranges[0] = ranges[1]

        elif(bound.side_num == 2):
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

        elif(bound.side_num == 3):
            xfrom = bound.region[0]
            xto = bound.region[1]
            yfrom = block.size.sizeY
            yto = block.size.sizeY

            intervalX = [xfrom, xto, model.grid.gridStepX]
            intervalY = [yfrom, yto, model.grid.gridStepY]
            ranges = getRangesInClosedInterval(intervalX, intervalY)

            # because yfrom == yto == sizeY
            # and Im(yfrom) == Im(sizeY) and Im(yto) == Im(sizeY)+1
            # make Im(yfrom) = Im(sizeY)+1 (==Im(yto))
            # ranges[2] = ranges[3]

        idx = [eq_num] + ranges
        return(idx)
