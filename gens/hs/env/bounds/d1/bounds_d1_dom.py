from gens.hs.env.bounds.common.bounds_common_dom import GenBaseDomCommon
from gens.hs.env.base.base_common import Params

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.bounds_dom_1d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('bounds_dom_1d')
logger.setLevel(level=log_level)
'''


class GenDomD1(GenBaseDomCommon):

    def __init__(self, net):
        self.net = net
        self.params = Params()

    def set_params_for_dom_bounds(self, model,
                                  namesAndNumbers, functionMaps):
        '''
        DESCRIPTION:

        Add bounds data for 1d dom to ``functionMaps`` dict.

        Inputs:

        - ``self.net.params.bounds_edges`` -- from \
        ``self.net.common.set_params_for_bounds``

        - ``namesAndNumbers`` -- from::

           ``array_common.py: set_params_for_array``
           ``cent_common.py: set_params_for_centrals``
           ``ics_common.py: set_params_for_interconnects``
           ``bounds_common.py: set_params_for_bounds``

        ``namesAndNumbers`` is copy of ``pBoundFuncs`` of
        ``getBlockBoundFuncArray`` function.
        It contain func names at according position
        and used for getting right number of equations in domain file.
        '''
        dim = model.dimension
        self.params.namesAndNumbers = namesAndNumbers
        self.params.functionMaps = functionMaps

        self.set_params_for_dom_common(dim, model)

    def get_idx(self, model, bound):
        '''
        DESCRIPTION:

        Get ``idx`` for ``bound.side``. For 1d.

        RETURN:

        equation number
        '''
        namesAndNumbers = self.params.namesAndNumbers
        eq_num = namesAndNumbers[bound.blockNumber].index(bound.funcName)

        idx = eq_num
        return(idx)
