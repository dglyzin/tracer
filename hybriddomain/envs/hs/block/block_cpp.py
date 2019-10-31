from hybriddomain.spaces.some_space.someFuncs import getCellCountInClosedInterval


class BlockCpp():
    def __init__(self, net):
        self.net = net
    
    def get_grid_offsets(self):
        size = self.net.size
        try:
            # 3d
            return([size.offsetX, size.offsetY, size.offsetZ])
        except:
            try:
                # 2d
                return([size.offsetX, size.offsetY, 0])
            except:
                # 1d
                return([size.offsetX, 0, 0])

    def get_grid_sizes(self):
        size = self.net.size

        try:
            # 3d
            return([size.sizeX, size.sizeY, size.sizeZ])
        except:
            try:
                # 2d
                return([size.sizeX, size.sizeY, 0])
            except:
                # 1d
                return([size.sizeX, 0, 0])

    def get_block_args(self, model):
        grid = model.grid.cpp
        gridStep = grid.get_grid_step()
        
        class Args():
            '''
            DESCRIPTION:
            Class for storage args data
            for code simplification reason.
            '''
            def __init__(self):
                pass

        blockArgs = Args()
        blockArgs.blockNumber = self.net.blockNumber
        
        blockArgs.cellsize = self.net.size.get_cell_size(model)

        # for each var in vars grid step exist
        countOfVars = len(gridStep)

        # for counts
        counts = []
        for i in range(countOfVars):
            d = gridStep[i]
            sizeForIndepVar = self.get_grid_sizes()[i]
            countOfGridStepsInVar = getCellCountInClosedInterval(sizeForIndepVar, d)
            counts.append(countOfGridStepsInVar)

        # for strides
        strides = []
        for i in range(countOfVars):
            if i == 0:
                stride = 1
            elif i == 1:
                stride = counts[0]
            else:
                # if i == 2
                stride = counts[0] * counts[1]
            strides.append(stride)
        
        defaultIndepVars = ['x', 'y', 'z']
        blockArgs.indepVars = defaultIndepVars
        blockArgs.counts = counts
        blockArgs.strides = strides
        blockArgs.offsets = self.get_grid_offsets()
        
        return(blockArgs)
