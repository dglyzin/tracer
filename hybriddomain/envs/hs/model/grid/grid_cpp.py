class GridCpp():
    def __init__(self, net):
        self.net = net

    def get_grid_step(self):
        gridStep = [self.net.gridStepX, self.net.gridStepY,
                    self.net.gridStepZ]
        # FOR ERRORS
        if len(gridStep) < 3:
            raise AttributeError("A list 'gridStep' should be consist of"
                                 + " values for ALL independent variables!"
                                 + " x, y, z")
        # END FOR ERRORS

        return(gridStep)
   
    def get_grid_args(self):
        gridStep = self.get_grid_step()

        class Args():
            '''
            DESCRIPTION:
            Class for storage args data
            for code simplification reason.
            '''
            def __init__(self):
                pass

        defaultIndepVars = ['x', 'y', 'z']

        gridArgs = []
        for i in range(len(gridStep)):
            gridArg = Args()
            gridArg.indepVar = defaultIndepVars[i]
            d = gridStep[i]
            gridArg.d = d
            gridArg.d2 = round(d * d, 5)
            gridArg.dm1 = round(1 / d)
            gridArg.dm2 = round(1 / (d * d))
            gridArgs.append(gridArg)
        return(gridArgs)

