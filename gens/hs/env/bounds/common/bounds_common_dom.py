import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('bounds.bounds_common_dom')

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
        Add bounds data for dom to ``functionMaps`` dict::

        ``self.net.params from``
        ``self.net.common.set_params_for_bounds``'''

        functionMaps = self.params.functionMaps

        # bounds sides
        for bound in self.net.params.bounds:
            sideName = "side"+str(bound.side_num)

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

    def _get_idx(self, model, bound):
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
