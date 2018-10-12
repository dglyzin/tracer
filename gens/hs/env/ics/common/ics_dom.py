from math_space.common.someClasses import Params

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


class GenDomCommon():
    
    def __init__(self, net):
        self.net = net
        self.params = Params()

    def set_params_for_dom_interconnects(self, model,
                                         namesAndNumbers, functionMaps):
        '''
        DESCRIPTION::

        Add ics data for 1d, 2d dom to
        ``functionMaps`` dict.

        Inputs:

        :param self.net.params:  from::

           ``ics_common.py: set_params_for_dom_interconnects``

        :param namesAndNumbers:  from::

           ``array_common.py: set_params_for_array``
           ``cent_common.py: set_params_for_centrals``
           ``ics_common.py: set_params_for_interconnects``
           ``bounds_common.py: set_params_for_bounds``
        '''
        # interconnect
        # logger.debug("namesAndNumbers = %s" % (namesAndNumbers[0]))

        self.params.functionMaps = functionMaps
        ics = self.net.params

        logger.debug("len(ics) = %s" % (len(ics)))

        for ic in ics:
            sideName = "side"+str(ic.side_num)
            
            # count of interconnects for each block
            idx = namesAndNumbers[ic.blockNumber].index(ic.funcName)
            logger.debug("funcName=%s " % str(ic.funcName))
            logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))
            
            if model.dimension == 1:
                value_to_update = idx

            elif model.dimension == 2:
                value_to_update = [idx] + ic.ranges

            # update functionMaps:
            if sideName not in functionMaps[ic.blockNumber].keys():
                functionMaps[ic.blockNumber].update({sideName:
                                                     value_to_update})
