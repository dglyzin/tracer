import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.blocks_filler_1d')

# if using directly uncoment that:
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('init_funcs_nums.py')
logger.setLevel(level=log_level)

bdict = {"dirichlet": 0, "neumann": 1}


class InitFuncsNums():
    def __init__(self, model, block):

        # FOR defaultInitial:
        usedInitNums = [block.defaultInitial]
        self.usedInitNums_di = usedInitNums[:]
        logger.debug("Used for init nums defaultInitial:")
        logger.debug(self.usedInitNums_di)

        # END FOR

        # FOR initialRegions:
        # collect user-defines initial conditions
        # that are used in this block
        for iRegion in block.initialRegions:
            if not (iRegion.initialNumber in usedInitNums):
                usedInitNums.append(iRegion.initialNumber)
        self.usedInitNums_ir = usedInitNums[:]
        logger.debug("Used for init nums initial region:")
        logger.debug(self.usedInitNums_ir)
        # END FOR        

        # FOR dirichlet boundRegions:
        self.usedIndices = len(usedInitNums)
        usedDirBoundNums = []
        for side_num in block.boundRegions:
            for bound in block.boundRegions[side_num]:
                boundNumber = bound.boundNumber
                if not (boundNumber in usedDirBoundNums):
                    bound_btype = model.bounds[boundNumber].btype
                    if (bound_btype == bdict["dirichlet"]):
                        usedDirBoundNums.append(boundNumber)
        usedDirBoundNums.sort()
        self.usedDirBoundNums = usedDirBoundNums
        logger.debug("Used for init nums dirichlet bound regions:")
        logger.debug(self.usedDirBoundNums)
        # END FOR

    def get_default_initial(self, defaultInitial):
        return(self.usedInitNums_di.index(defaultInitial))
        
    def get_initial_regions(self, initialNumber):
        return(self.usedInitNums_ir.index(initialNumber))

    def get_dirichlet_bound_regions(self, boundNumber):
        
        '''for initFuncArray indexes
        factorization dirichlet/undirichlet
        '''
        return((self.usedIndices + self.usedDirBoundNums.index(boundNumber)))
