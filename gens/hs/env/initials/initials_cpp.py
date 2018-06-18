from gens.hs.env.base.base_common import Params


class GenCpp():
        
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_initials(self, model):
        '''
        DESCRIPTION:
        
        Collecting this parameters:

        self.net.params.dim
        self.net.params.blocks

        USED PARAMETERS:
        model.blocks
        model.initials
        model.bounds
        '''
        # FOR FILL model.blocks
        for block in model.blocks:

            # for Dirichlet
            # set() used for removing duplicates
            fDirichletIndexes = list(
                set(
                    [bR.boundNumber
                     for k in block.boundRegions
                     for bR in block.boundRegions[k]
                     if (model.bounds[bR.boundNumber].btype == 0)]))
            block.fDirichletIndexes = fDirichletIndexes

            # for initials
            block.initialIndexes = list(
                set(
                    [iR.initialNumber
                     for iR in block.initialRegions
                     if iR.initialNumber != block.defaultInitial]))

            # copy initials uniquely:
            block.initialIndexes = list(
                set(
                    [iR.initialNumber
                     for iR in block.initialRegions
                     if iR.initialNumber != block.defaultInitial]))
            block.initials = [model.initials[idx]
                              for idx in block.initialIndexes]

            # copy bounds uniquely:
            bounds = [model.bounds[idx]
                      for idx in block.fDirichletIndexes]
            block.bounds = []
            for bound in bounds:
                if bound not in block.bounds:
                    block.bounds.append(bound)

            # FOR parser:
            for initial in block.initials:
                initial.parsedValues = initial.values

            for bound in block.bounds:
                bound.parsedValues = [value  # parser.parseMathExpression(value)
                                      for value in bound.values]
            # END FOR

        self.net.params.dim = model.dimension
        self.net.params.blocks = model.blocks
