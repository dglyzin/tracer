from math_space.common.someClasses import Params
from gens.hs.common.init_funcs_nums import InitFuncsNums

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('initials_main.initials_cpp')
'''
# if using directly uncoment that:
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('initials_cpp.py')
logger.setLevel(level=log_level)
'''

class GenCpp():
        
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_initials(self, model):
        '''
        DESCRIPTION::
        
        Collecting this parameters::

            ``self.net.params.dim``
            ``self.net.params.blocks``

        USED PARAMETERS::

            ``model.blocks``
            ``model.initials``
            ``model.bounds``
        '''
        # FOR FILL model.blocks
        for block in model.blocks:

            ifn = InitFuncsNums(model, block)

            '''
            # for initials
            block.initialIndexes = ifn.usedInitNums_ir[:]
            logger.debug("initialIndexes:")
            logger.debug(block.initialIndexes)

            # for Dirichlet
            block.fDirichletIndexes = [
                ifn.get_dirichlet_bound_regions(boundNumber)
                for boundNumber in ifn.usedDirBoundNums]
            logger.debug("fDirichletIndexes:")
            logger.debug(block.fDirichletIndexes)
            '''
            '''
            block.fDirichletIndexes = [
                ifn.get_dirichlet_bound_regions(bR.boundNumber)
                for k in block.boundRegions
                for bR in block.boundRegions[k]
                if (model.bounds[bR.boundNumber].btype == 0)]
            '''
            '''
            # set() used for removing duplicates
            fDirichletIndexes = list(
                set(
                    [bR.boundNumber
                     for k in block.boundRegions
                     for bR in block.boundRegions[k]
                     if (model.bounds[bR.boundNumber].btype == 0)]))
            block.fDirichletIndexes = fDirichletIndexes
            '''
            '''
            # for initials
            block.initialIndexes = list(
                set(
                    [iR.initialNumber
                     for iR in block.initialRegions]))
            # if iR.initialNumber != block.defaultInitial
            '''
            '''
            # copy initials uniquely:
            block.initialIndexes = [block.defaultInitial]

            for iR in block.initialRegions:
                if iR.initialNumber not in block.initialIndexes:
                    block.initialIndexes.append(iR.initialNumber)
            '''
            '''
            block.initialIndexes = list(
                set(
                    [iR.initialNumber
                     for iR in block.initialRegions]))
            # if iR.initialNumber != block.defaultInitial
            '''

            def take(regions, regionsIndexes, getter):
                
                '''Take initials or bounds, with original indexes
                from regionsIndexes. Map original indexes to
                getInitFuncArray using getter'''
                
                for idx, regionIndex in enumerate(regionsIndexes):
                    region = regions[regionIndex]
                    region.idx = getter(regionIndex)
                    yield(region)

            # copy initials:
            getter = lambda idx: ifn.get_initial_regions(idx)
            block.initials = [initial
                              for initial in take(model.initials,
                                                  ifn.usedInitNums_ir,
                                                  getter)]
            logger.debug("block.initials:")
            logger.debug(block.initials)

            # copy bounds:
            # fDirichletIndexes and bounds has same structure
            # (len and indexes) due to common ifn.usedDirBoundNums
            getter = lambda idx: ifn.get_dirichlet_bound_regions(idx)
            bounds = [bound
                      for bound in take(model.bounds,
                                        ifn.usedDirBoundNums,
                                        getter)]
            block.bounds = bounds

            # FOR parser:
            for initial in block.initials:
                initial.parsedValues = initial.values
                logger.debug("initial.parsedValues:")
                logger.debug(initial.parsedValues)

            for bound in block.bounds:
                bound.parsedValues = [value  # parser.parseMathExpression(value)
                                      for value in bound.values]
            # END FOR

        self.net.params.dim = model.dimension
        self.net.params.blocks = model.blocks
