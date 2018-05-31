from envs.hs.model.grid.grid_base import GridBase
from envs.hs.model.grid.grid_cpp import GridCpp


class GridNet():
    '''
    '''
    def __init__(self, name=None, blockNumber=0, size=None, sides=[],
                 bRegions=[], eRegions=[], iRegions=[]):

        self.base = GridBase(self)
        # self.io = BlockIO(self)
        self.cpp = GridCpp(self)

    def __repr__(self):
        out = ""
        attrs = self.__dict__
        for key_atr in attrs.keys():
            out += key_atr + ":" + str(attrs[key_atr]) + "\n"
        return(out)

