from gens.hs.env.base.base_common import GenBaseCommon
from gens.hs.env.base.base_common import Params


class GenCommon(GenBaseCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_definitions(self, model):
        '''
        DESCRIPTION:
        Fill params for definitions 1d template.
        '''
        grid_cpp = model.grid.cpp

        gridArgs = grid_cpp.get_grid_args()

        # FOR define block (mainly with stride and counts)
        blocksArgs = []
        for blockNumber, block in enumerate(model.blocks):
            blocksArgs.append(block.cpp.get_block_args(model))
        # END FOR stride and counts

        self.net.params.gridArgs = gridArgs
        self.net.params.blocksArgs = blocksArgs
        self.net.params.paramsLen = len(model.params)
        self.net.params.timeStep = model.solver.timeStep

