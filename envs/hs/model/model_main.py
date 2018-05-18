from envs.hs.model.model_base import ModelBase
from envs.hs.model.model_io import ModelIO
from envs.hs.model.model_device import ModelDevice
from envs.hs.model.model_gen_cpp import ModelGenCpp
from envs.hs.model.model_editor import ModelEditor
from envs.hs.model.grid import Grid


class Tmp():
    def __repr__(self):
        out = ""
        attrs = self.__dict__
        for key_atr in attrs.keys():
            out += key_atr + ":" + str(attrs[key_atr]) + "\n"
        return(out)


class ModelNet():

    # model = Model(grid, blocks=[block1,...], ics=[ic1,...])
    def __init__(self, grid=None, blocks=None, ics=None):
        if grid is None:
            self.grid = Grid()
        else:
            self.grid = grid
        self.solver = Tmp()

        self.blocks = blocks
        
        self.ics = ics

        self.base = ModelBase(self)
        self.io = ModelIO(self)
        self.device = ModelDevice(self)
        self.editor = ModelEditor(self)
        self.cpp = ModelGenCpp(self)
        self.domain = None

    def show(self):
        return(self.base.toDict())
