from gens.hs.env.base.base_common import Params


class GenDom():

    def __init__(self, net):
        self.net = net
        self.params = Params()

    def set_params_for_dom_centrals(self, model,
                                    namesAndNumbers, functionMaps):
        '''
        DESCRIPTION::

        Add bounds data for 1d dom to ``functionMaps`` dict.
        Mapping equations to block parts
        like
         ``center: [  [ 1, xfrom, xto, yfrom, yto]``,
        means equation[1] for part
         ``(xfrom, yfrom), (xto, yto)``

        Inputs:

        :param self.net.params: from::

           ``bounds_common_1d.py: set_params_for_dom_bounds``

        :param namesAndNumbers: from::

           ``array_common.py: set_params_for_array``
           ``cent_common.py: set_params_for_centrals``
           ``ics_common.py: set_params_for_interconnects``
           ``bounds_common.py: set_params_for_bounds``

        '''
        '''
        # check if functionMaps alredy exist:
        if 'functionMaps' not in self.net.params.__dict__:
            self.net.params.functionMaps = []
        '''
        # dim = model.dimension
        self.params.functionMaps = functionMaps

        for blockNumber, block in enumerate(model.blocks):

            blockFuncMap = {'center': []}
            for eParam in self.net.params:
                if eParam.blockNumber == blockNumber:
                    eq_num = namesAndNumbers[eParam.blockNumber].index(eParam.funcName)
                    if eParam.default:
                        blockFuncMap['center_default'] = eq_num
                    else:
                        ranges = model.grid.dom.get_ranges(eParam.eRegion)
                        blockFuncMap['center'].append([eq_num]+ranges)
            '''
            # split equations at regions
            for eRegion in block.equationRegions:
                reservedSpace = acc(eRegion, reservedSpace)

                # for removing trivial cases
                cond = (eRegion.xfrom == eRegion.xto
                        and
                        (eRegion.xto == 0.0 or eRegion.xto == block.sizeX))

                
                if eRegion.equationNumber not in numsForSystems and not cond:
                    numsForSystems.append(eRegion.equationNumber)
                if not cond:
                    # see getRangesInClosedInterval description
                    ranges = get_ranges(eRegion)
                    # blockFuncMap['center'].append([eq_num] + ranges)
                    blockFuncMap['center'].append([numsForSystems.index(eRegion.equationNumber)] + ranges)
            
            # add default equation at remaining regions.
            if do_generate_default(reservedSpace, block):
                # add last as default
                blockFuncMap.update({'center_default': len(numsForSystems)})
                numsForSystems.append(block.defaultEquation)
            '''
            
            self.params.functionMaps[blockNumber] = blockFuncMap
