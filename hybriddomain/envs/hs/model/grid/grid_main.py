from hybriddomain.envs.hs.model.grid.grid_base import GridBase
from hybriddomain.envs.hs.model.grid.grid_cpp import GridCpp
from hybriddomain.envs.hs.model.grid.grid_dom import GridDom


class GridNet():
    '''
    '''
    def __init__(self, name=None, blockNumber=0, size=None,
                 sides=[], bRegions=[], eRegions=[], iRegions=[]):

        self.base = GridBase(self)
        # self.io = BlockIO(self)
        self.cpp = GridCpp(self)
        self.dom = GridDom(self)

    def __repr__(self):
        out = ""
        attrs = self.__dict__
        for key_atr in attrs.keys():
            out += key_atr + ":" + str(attrs[key_atr]) + "\n"
        return(out)

    def set_model(self, model):
        self.model = model
