from gens.hs.gen_env.cpp.env.base.base_common import GenBaseCommon
from gens.hs.gen_env.cpp.env.ics.common.ics_common_cpp import GenCppCommon
from spaces.some_space.someClasses import Params
from spaces.some_space.someFuncs import determineNameOfBoundary

from functools import reduce


class GenCommonD2(GenBaseCommon, GenCppCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_interconnects(self, model, funcNamesStack):
        '''
        DESCRIPTION::

        Collect this parameters for template::
        
        ``ic.funcName``
        ``ic.boundName``
        ``ic.blockNumber``
        ``ic.parsedValues``
        ``ic.original``
        unique according to ``ic.funcName``

        Collect this parameters for ``functionMaps``
        (in block.sides ic intervals as 'fm' key)::
        
        ``ic.funcName``
        ``ic.side_num``
        ``ic.ranges``
        '''
        ics = []

        ics = [icr
               for block in model.blocks
               for side_num in block.sides
               for icr in self.set_params_for_side(model,
                                                   block.sides[side_num])]
        '''
        ics = [icr
               for ic in model.interconnects
               for region_num in ic.regions
               for icr in self.set_params_for_block(model,
                                                    ic.regions[region_num])]
        '''

        # remove duplicates according to
        # ic.funcName uniqueness:
        ics = list(reduce(lambda acc, x: acc+[x]
                          if (x.funcName not in [ic.funcName for ic in acc])
                          else acc, ics, []))
        
        # ics_names = [icl.funcName for icl in ics]
        # logger.debug("icsOld = %s" % str(icsOld))
        # if ic.funcName not in ics_names:
        #     ics.append(ic)

        self.net.params.extend(ics)
                
        self.net.params.ics = ics
        # END FOR FILL

        # FOR FuncArray
        funcNamesStackLocal = [ic.funcName for ic in ics]
        self.fill_func_names_stack(funcNamesStack, funcNamesStackLocal)
        # END FOR

    def set_params_for_side(self, model, side):
        
        ics = []

        for interval in side.intervals:
            
            # if no interconnect then continue:
            try:
                interval.name['i']
            except KeyError:
                continue

            equationNumber = interval.name['e']
            equation = model.equations[equationNumber].copy()
        
            icRegion = interval.name['i']()

            blockNumber = icRegion.blockNumber
            side_num = icRegion.side_num

            funcName = ("Block" + str(blockNumber)
                        + "Interconnect__Side" + str(side_num)
                        + "_Eqn" + str(equationNumber))

            # generate equation:
            parsedValues = self.parse_equations(equation, model.dimension,
                                                blockNumber, side_num,
                                                icRegion.firstIndex,
                                                icRegion.secondIndex)
            # fill params:
            ic = Params()
            ic.name = "Connection"
            # ic.firstIndex = icRegion.firstIndex
            # ic.secondIndex = icRegion.secondIndex
            ic.side_num = side_num
            # ic.ranges = icRegion.ranges
            # ic.equationNumber = equationNum
            ic.equation = equation
            ic.funcName = funcName
            ic.boundName = determineNameOfBoundary(side_num)
            ic.blockNumber = blockNumber
            ic.parsedValues = parsedValues
            ic.original = [e.sent for e in equation.eqs]

            # for functionMaps:
            interval.name['fm'] = ic

            # for cpp:
            # each block can connect to many other block
            # let other block discribe interconnect in
            # that case
            ics.append(ic)

        return(ics)
