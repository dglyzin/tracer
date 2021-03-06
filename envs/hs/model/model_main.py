from envs.hs.model.model_base import ModelBase
from envs.hs.model.model_io import ModelIO
from envs.hs.model.model_device import ModelDevice
from envs.hs.model.cpp.model_gen_cpp import ModelGenCpp
from envs.hs.model.model_editor import ModelEditor
from envs.hs.model.grid.grid_main import GridNet as Grid

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('model_main.model_device')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('model_main')
logger.setLevel(level=log_level)


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
        self.grid.set_model(self)
        
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
