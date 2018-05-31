from gens.hs.cpp.common.base import GenBase


class Gen(GenBase):

    def get_out_for_definitions(self):
        template = self.env.get_template('definitions.template')
        params = self
        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)
    
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

        self.gridArgs = gridArgs
        self.blocksArgs = blocksArgs
        self.paramsLen = len(model.params)
        self.timeStep = model.solver.timeStep

