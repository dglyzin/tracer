import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.bounds_common_dom')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('bounds_common_dom')
logger.setLevel(level=log_level)
'''


class GenBaseDomCommon():

    '''Base for 1d and 2d dom methods'''

    def set_params_for_dom_common(self, dim, model):
        
        '''
        Add bounds data for dom to functionMaps dict.

        self.net.params from
        self.net.common.set_params_for_bounds'''

        functionMaps = self.params.functionMaps

        # bounds sides
        for bound in self.net.params:
            sideName = "side"+str(bound.side)

            # for setDomain
            idx = self._get_idx(model, bound)
            logger.debug("funcName=%s " % str(bound.funcName))
            logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))

            old = functionMaps[bound.blockNumber]
            if sideName in old.keys():
                # if side exist
                functionMaps[bound.blockNumber][sideName].append(idx)
            else:
                # because in 2d side will be list
                if dim == 1:
                    functionMaps[bound.blockNumber].update({sideName: idx})
                elif dim == 2:
                    functionMaps[bound.blockNumber].update({sideName: [idx]})
