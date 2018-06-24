from gens.hs.gen_1d import GenD1
from gens.hs.gen_sh import GenSH
from gens.hs.fiocr.fiocr_main import Fiocr

from envs.hs.model.model_main import ModelNet as Model


class Gen():
    def __init__(self, model, settings):
        # model="tests/test1d_two_blocks0.json"

        # model:
        if type(model) == str:
            oModel = Model()
            oModel.io.loadFromFile(model)
            self.model = oModel
        else:
            self.model = model

        # settings:
        self.settings = settings
        self.settings.make_all_pathes(self.model)

        # choice gen type:
        if self.model.dimension == 1:
            self.gen_dim = GenD1(self)
        
        # sh gen:
        self.gen_sh = GenSH(self)

        # file io compilation routine:
        self.fiocr = Fiocr()

    def gen_all(self):
        
        '''Generate cpp and dom files.'''

        self.gen_dim.gen_cpp()
        self.gen_dim.gen_arrays()

    def save_all(self):

        '''Save all files. Cleare all.'''

        pathes = self.settings.pathes

        self.fiocr.create_out(pathes['hd']['out_folder'],
                              pathes['hd']['userfuncs'])

        # save cpp:
        self.fiocr.to_file(self.gen_dim.cpp_out, pathes['hd']['cpp'])

        # generage so:
        self.fiocr.make_gcc_so(pathes['hd']['cpp'], pathes['hd']['so'])

        # save dom txt:
        self.gen_dim.filler.save_txt(pathes['hd']['dom_txt'])

        # save dom bin:
        self.gen_dim.filler.save_bin(pathes['hd']['dom_bin'])

        # create sh file:
        self.gen_sh.set_params(self.settings.device_conf['default'])
        self.gen_sh.gen_sh(self.settings.pathes['hd']['sh'])
