from gens.hs.cpp.common.base import GenBase


class Gen(GenBase):
    '''
    Fill self.params for initials template:
    (see self.set_params_for_initials)

    Generate cpp:
    (see get_out_for_initials)
    '''

    def get_out_for_initials(self):
        template = self.env.get_template('initial_conditions.template')
        params = self

        args = {
            'blocks': params.blocks,
            'dim': params.dim,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)
    
    def set_params_for_initials(self, model):
        '''
        DESCRIPTION:
        Fill parameters for .cpp initial and Dirichlet functions.
        for cppOutsForGenerators.get_out_for_initials

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
        
