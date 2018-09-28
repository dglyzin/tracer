from gens.hs.env.base.base_common import GenBaseCommon
from gens.hs.env.base.base_common import Params
from math_space.common.someFuncs import determineNameOfBoundary


class GenCommon(GenBaseCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_interconnects(self, model, funcNamesStack):
        #   (self, mainBlockSide, mainBlock, secBlock, firstIndex):
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
        if mainBlockSide == 0:
            xfrom = 0#mainBlock.offsetX
            xto = 0#mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[1]
        elif mainBlockSide == 1:
            xfrom = mainBlock.sizeX# + mainBlock.offsetX
            xto = mainBlock.sizeX# + mainBlock.offsetX
            yfrom = max([secBlock.offsetY, mainBlock.offsetY]) - mainBlock.offsetY
            yto = min([mainBlock.offsetY + mainBlock.sizeY, secBlock.offsetY + secBlock.sizeY]) - mainBlock.offsetY
            someLen = yfrom
            lenOfConnection = yto - yfrom
            secondIndex = 'idxY'
            stepAlongSide = self.gridStep[1]
        elif mainBlockSide == 2:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = 0#mainBlock.offsetY
            yto = 0#mainBlock.offsetY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[0]
        else:
            xfrom = max([mainBlock.offsetX, secBlock.offsetX]) - mainBlock.offsetX
            xto = min([mainBlock.offsetX + mainBlock.sizeX, secBlock.offsetX + secBlock.sizeX]) - mainBlock.offsetX
            yfrom = mainBlock.sizeY# + mainBlock.offsetY
            yto = mainBlock.sizeY# + mainBlock.offsetY
            someLen = xfrom
            lenOfConnection = xto - xfrom
            secondIndex = 'idxX'
            stepAlongSide = self.gridStep[0]
        return InterconnectRegion(firstIndex, secondIndex, mainBlockSide, stepAlongSide, someLen, lenOfConnection, xfrom, xto, yfrom, yto, self.blocks.index(secBlock))
        # ranges (xfrom, xto,...) used in functionMaps
        # sideLst.append([arrWithFunctionNames.index(condition.funcName)] + ranges)
        #    # for saveDomain
        #    blockFunctionMap.update({sideName:sideLst}) 
