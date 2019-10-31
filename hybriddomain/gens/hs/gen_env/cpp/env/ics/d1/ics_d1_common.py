from hybriddomain.gens.hs.gen_env.cpp.env.base.base_common import GenBaseCommon
from hybriddomain.gens.hs.gen_env.cpp.env.ics.common.ics_common_cpp import GenCppCommon
from hybriddomain.spaces.some_space.someClasses import Params
from hybriddomain.spaces.some_space.someFuncs import determineNameOfBoundary


class GenCommonD1(GenBaseCommon, GenCppCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_interconnects(self, model, funcNamesStack):
        '''
        DESCRIPTION::

        Collect this parameters for template::
        
        ``ic.firstIndex``
        ``ic.secondIndex``
        ``ic.side``
        ``ic.ranges``
        ``ic.equationNumber``
        ``ic.equation``
        ``ic.funcName``
        ``ic.boundName``
        ``ic.blockNumber``
        ``ic.parsedValues``
        ``ic.original``

        '''
        # FOR FILL params.ics
        self.net.params = Params()
        ics = []
    
        for blockNumber, block in enumerate(model.blocks):
            for iconn in model.interconnects:
                # for closed block
                if iconn.block1 == blockNumber and iconn.block2 == blockNumber:

                    self.check_firstIndex(block)

                    ic1, ic2 = (self
                                ._set_params_for_closed_block(model, block,
                                                              iconn, blockNumber,
                                                              block.firstIndex+1,
                                                              block.firstIndex))
                    block.firstIndex += 2

                    # for functionMaps:
                    block.vertexs['[0]'].fm = ic1
                    block.vertexs['[1]'].fm = ic2

                    # for cpp:
                    ics.append(ic1)
                    ics.append(ic2)

                # for differ blocks
                elif blockNumber in [iconn.block1, iconn.block2]:
                    self.check_firstIndex(block)

                    ic = self._set_params_for_two_blocks(model, block,
                                                         iconn, ics,
                                                         blockNumber,
                                                         block.firstIndex)
                    block.firstIndex += 1

                    # for functionMaps:
                    block.vertexs['['+str(ic.side_num)+']'].fm = ic

                    icsOld = [icl.funcName for icl in ics]
                    # logger.debug("icsOld = %s" % str(icsOld))
                    if ic.funcName not in icsOld:
                        # for cpp:
                        ics.append(ic)
                else:
                    continue

        self.net.params.ics = ics
        # END FOR FILL

        # FOR FuncArray
        funcNamesStackLocal = [ic.funcName for ic in ics]
        self.fill_func_names_stack(funcNamesStack, funcNamesStackLocal)
        # END FOR

    def _set_params_for_two_blocks(self, model, block, iconn, ics,
                                   blockNumber, firstIndex):
        '''Only for one block in pair.'''
        # choice side:
        if (iconn.block1 == blockNumber
            and iconn.block2 != blockNumber):
            # case differ 1
            side_num = iconn.block1Side
        elif (iconn.block2 == blockNumber
              and iconn.block1 != blockNumber):
            # case differ 2
            side_num = iconn.block2Side

        # len(ics for block)
        # firstIndex = len(ics)

        # FOR find equation for block
        Range = (side_num == 1) * block.size.sizeX
        coord = lambda region: ((side_num == 0) * region.xfrom
                                + (side_num == 1) * region.xto)
        side_test = lambda eRegion: coord(eRegion) == Range
        equationNum = self.choice_equation_num(side_test, block)

        equation = model.equations[equationNum].copy()
        # END FOR

        funcName = ("Block" + str(blockNumber)
                    + "Interconnect__Side" + str(side_num)
                    + "_Eqn" + str(equationNum))

        # generate equation:
        parsedValues = self.parse_equations(equation, model.dimension,
                                            blockNumber, side_num,
                                            firstIndex, 0)
        # fill params:
        ic = Params()
        ic.name = "Connection"
        ic.firstIndex = firstIndex
        ic.secondIndex = '0'
        ic.side_num = side_num
        ic.ranges = []
        ic.equationNumber = equationNum
        ic.equation = equation
        ic.funcName = funcName
        ic.boundName = determineNameOfBoundary(side_num)
        ic.blockNumber = blockNumber
        ic.parsedValues = parsedValues
        ic.original = [e.sent for e in equation.eqs]
        
        # each block can connect to many other block
        # let other block discribe interconnect in
        # that case
        return(ic)

    def _set_params_for_closed_block(self, model, block, iconn,
                                     blockNumber, srcFirstIndex,
                                     distFirstIndex):

        '''srcFirstIndex and distFirstIndex is first indexes of
        two interconects of same block'''

        # FOR finding equations:
        # choice left or right side of block
        # i.e. 0.0 or block.sizeX
        Range1 = (iconn.block1Side == 1) * block.size.sizeX
        Range2 = (iconn.block2Side == 1) * block.size.sizeX

        # return either xfrom or xto for block
        coord1 = lambda region: ((iconn.block1Side == 0)
                                 * region.xfrom
                                 + (iconn.block1Side == 1)
                                 * region.xto)
        coord2 = lambda region: ((iconn.block2Side == 0)
                                 * region.xfrom
                                 + (iconn.block2Side == 1)
                                 * region.xto)

        # find equation
        # for first block (one side of closed block)
        side_test = lambda eRegion: coord1(eRegion) == Range1
        equationNum1 = self.choice_equation_num(side_test, block)

        # find equation
        # for second block (other side of closed block)
        side_test = lambda eRegion: coord2(eRegion) == Range2
        equationNum2 = self.choice_equation_num(side_test, block)

        equation1 = model.equations[equationNum1].copy()
        equation2 = model.equations[equationNum2].copy()
        # END FOR

        funcName1 = ("Block" + str(blockNumber)
                     + "Interconnect__Side"
                     + str(iconn.block1Side)
                     + "_Eqn" + str(equationNum1))
        funcName2 = ("Block" + str(blockNumber)
                     + "Interconnect__Side"
                     + str(iconn.block2Side)
                     + "_Eqn" + str(equationNum2))

        # FOR equatioin cpp:
        # first equation:
        parsedValues_1 = self.parse_equations(equation1, model.dimension,
                                              blockNumber, iconn.block1Side,
                                              1, 0)

        # second equation:
        parsedValues_2 = self.parse_equations(equation2, model.dimension,
                                              blockNumber, iconn.block2Side,
                                              0, 0)
        # END FOR

        # fill params:
        ic1 = Params()
        ic1.name = "Connection"
        ic1.firstIndex = srcFirstIndex
        ic1.secondIndex = '0'
        ic1.side_num = iconn.block1Side
        ic1.ranges = []
        ic1.equationNumber = equationNum1
        ic1.equation = equation1
        ic1.funcName = funcName1
        ic1.parsedValues = parsedValues_1
        ic1.original = [e.sent for e in equation1.eqs]
        ic1.boundName = determineNameOfBoundary(iconn.block1Side)
        ic1.blockNumber = blockNumber
        
        ic2 = Params()
        ic2.name = "Connection"
        ic2.firstIndex = distFirstIndex
        ic2.secondIndex = '0'
        ic2.side_num = iconn.block2Side
        ic2.ranges = []
        ic2.equationNumber = equationNum2
        ic2.equation = equation2
        ic2.funcName = funcName2
        ic2.parsedValues = parsedValues_2
        ic2.original = [e.sent for e in equation2.eqs]
        ic2.boundName = determineNameOfBoundary(iconn.block2Side)
        ic2.blockNumber = blockNumber

        return((ic1, ic2))

    def check_firstIndex(self, block):
        
        try:
            block.firstIndex
        except AttributeError:
            block.firstIndex = 0
    
    def test(self, region, side_num, block):
        '''
        DESCRIPTION::

        Test if region exist for this side.
        '''
        if side_num == 0:
            # test for left side
            return(region.xfrom == 0.0)
        else:
            # test for right side
            return(region.xto == block.size.sizeX)

    def choice_equation_num(self, test, block):
        '''
        DESCRIPTION::

        Choice equation number from ``equationRegions``
        if any satisfy the test, else choice default.
        '''
        for eRegion in block.equationRegions:
            if test(eRegion):
                equationNum = eRegion.equationNumber
                break
        else:
            equationNum = block.defaultEquation
        return(equationNum)
