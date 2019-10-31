from hybriddomain.envs.hs.block.block_base import BlockBase
from hybriddomain.envs.hs.block.block_io import BlockIO
from hybriddomain.envs.hs.block.block_size import BlockSize
from hybriddomain.envs.hs.block.block_plot import BlockPlotter
from hybriddomain.envs.hs.block.block_editor import BlockEditor
from hybriddomain.envs.hs.block.block_cpp import BlockCpp

from functools import reduce

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('block_main.block_io')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('block_main')
logger.setLevel(level=log_level)


class BlockNet():
    '''Represent rectangle for model. Contain sides
    with boundRegions used for model bound conditions,
    equationRegions and initRegions (init conditions).
    self.editor used to edit all this.
    self.plotter for plot.
    self.io for load/save to json
    
    boundRegions and sides is dicts with keys is
    it's sides_nums
    '''
    def __init__(self, name=None, blockNumber=0, size=None, sides=[],
                 bRegions=[], eRegions=[], iRegions=[]):

        self.base = BlockBase(self, name, blockNumber)
        self.io = BlockIO(self)
        self.plotter = BlockPlotter(self)
        self.editor = BlockEditor(self)
        self.cpp = BlockCpp(self)

        if size is None:
            self.size = BlockSize(self)
            self.size.set_default()
        else:
            self.size = size
            self.size.net = self

        # init all state data:
        self.editor.init_state()

        # fill sides if they given:
        if len(sides) > 0:
            for side in sides:
                self.editor.add_or_edit_side(side)
        else:
            self.editor.set_sides_default()

        # fill regions after side was done:
        self.editor.fill_regions(bRegions, eRegions, iRegions)

        # fill vertexs:
        self.editor.set_vertexs()
    
    def __eq__(self, o):

        '''Equality is difined with all attributs, except blockNumber,
        because it depends only of order in model.blocks list'''

        cond = (self.size == o.size
                and self.sides == o.sides
                and self.boundRegions == o.boundRegions
                and self.equationRegions == o.equationRegions
                and self.initialRegions == o.initialRegions)
        return(cond)
    
    def __repr__(self):

        out = ""
        # attrs = self.__dict__
        # for key_atr in attrs.keys():
        out += "size: \n" + str(self.size) + "\n"
        out += "\n#####"

        out += "\neRegions: \n"
        succ = (lambda acc, x: acc + "eRegion %s \n" % str(x[0])
                + str(x[1]) + '\n')
        out += reduce(succ, enumerate(self.equationRegions), '')

        out += "\n#####"
        out += "\niRegions: \n"
        succ = (lambda acc, x: acc + "iRegion %s \n" % str(x[0])
                + str(x[1]) + '\n')
        out += reduce(succ, enumerate(self.initialRegions), '')

        out += "\n#####"
        out += "\nbRegions: \n"
        succ = (lambda acc, x: acc + "side_num %s \n" % str(x)
                + reduce(lambda acc, br: acc + str(br) + '\n',
                         self.boundRegions[x], '')
                + '\n')
        out += reduce(succ, self.boundRegions, '')

        out += "\n#####"
        out += "\nsides: \n"
        succ = (lambda acc, x: acc + "\nside %s\n" % str(x)
                + str(self.sides[x]) + '\n')
        out += reduce(succ, self.sides, '')
        out += "\n"
        return(out)
