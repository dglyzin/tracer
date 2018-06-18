from gens.hs.env.base.base_common import Params

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.ics_dom')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('ics_dom')
logger.setLevel(level=log_level)
'''


class GenDomD1():
    
    def __init__(self, net):
        self.net = net
        self.params = Params()

    def set_params_for_dom_interconnects(self, model,
                                         namesAndNumbers, functionMaps):
        '''
        DESCRIPTION:
        Add ics data for 1d dom to functionMaps dict.

        Inputs:
        self.net.params from
           ics_common.py: set_params_for_dom_interconnects

        namesAndNumbers from
           array_common.py: set_params_for_array
           cent_common.py: set_params_for_centrals
           ics_common.py: set_params_for_interconnects
           bounds_common.py: set_params_for_bounds
        '''
        # interconnect
        # logger.debug("namesAndNumbers = %s" % (namesAndNumbers[0]))

        self.params.functionMaps = functionMaps
        ics = self.net.params

        logger.debug("len(ics) = %s" % (len(ics)))

        for ic in ics:
            sideName = "side"+str(ic.side)
            
            # count of interconnects for each block
            idx = namesAndNumbers[ic.blockNumber].index(ic.funcName)
            logger.debug("funcName=%s " % str(ic.funcName))
            logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))

            # update functionMaps:
            if sideName not in functionMaps[ic.blockNumber].keys():
                functionMaps[ic.blockNumber].update({sideName: idx})
