from gens.hs.gen_1d import GenD1
from gens.hs.gen_sh import GenSH
from gens.hs.gen_plot import GenPlot
from gens.hs.fiocr.fiocr_main import Fiocr


class Gen():
    def __init__(self, model, settings):
        # model="tests/test1d_two_blocks0.json"

        self.model = model
        self.settings = settings

        # choice gen type:
        if self.model.dimension == 1:
            self.gen_dim = GenD1(self)
        
        # sh gen:
        self.gen_sh = GenSH(self)

        # file io compilation routine:
        self.fiocr = Fiocr()

        self.gen_plot = GenPlot(self)

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

        # save plot params:
        self.gen_plot.save(pathes['hd']['plot'])

        # create sh file:
        device_conf_name = self.settings.device_conf_name
        self.gen_sh.set_params(self.settings.device_conf[device_conf_name])
        self.gen_sh.gen_sh(self.settings.pathes['hd']['sh'])
