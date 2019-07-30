from gens.hs.gen_env.gen_dim import GenD1
from gens.hs.gen_env.gen_dim import GenD2
from gens.hs.gen_sh import GenSH
from gens.hs.gen_plot import GenPlot
from gens.hs.fiocr.fiocr_main import Fiocr
from gens.hs.arrays_filler.filler_main import Filler


class Gen():
    def __init__(self, model, settings):
        # model="tests/test1d_two_blocks0.json"

        self.model = model
        self.settings = settings

        # choice gen type:
        if self.model.dimension == 1:
            self.gen_dim = GenD1(self)
        elif self.model.dimension == 2:
            self.gen_dim = GenD2(self)

        # sh gen:
        self.gen_sh = GenSH(self)

        # file io compilation routine:
        self.fiocr = Fiocr()

        self.gen_plot = GenPlot(self)

    def gen_all(self):
        
        '''Generate cpp and dom files.
        Create ``self.filler``'''

        self.gen_dim.gen_cpp()
        self.gen_dim.gen_dom()

        # fill arrays:
        self.filler = Filler(self.model,
                             self.gen_dim.functionMaps,
                             self.gen_dim.funcNamesStack,
                             self.gen_dim.namesAndNumbers,
                             self.gen_dim.delays)
        self.filler.fill_arrays()

        # self.gen_dim.gen_arrays()

    def save_all(self):

        '''Save all files. Cleare all.
        Only after ``self.gen_all``'''

        paths = self.settings.paths

        self.fiocr.create_out(paths['hd']['out_folder'],
                              paths['hd']['userfuncs'])

        # save cpp:
        self.fiocr.to_file(self.gen_dim.cpp_out, paths['hd']['cpp'])

        # generage so:
        self.fiocr.make_gcc_so(paths['hd']['cpp'], paths['hd']['so'])

        # save dom txt:
        self.filler.save_txt(paths['hd']['dom_txt'],
                             paths['hd']['out_folder'])
        # self.gen_dim.filler.save_txt(paths['hd']['dom_txt'])

        # save dom bin:
        self.filler.save_bin(paths['hd']['dom_bin'])
        # self.gen_dim.filler.save_bin(paths['hd']['dom_bin'])

        # save plot params:
        self.gen_plot.save(paths['hd']['plot'])

        # create sh file:
        self.gen_sh.set_params(self.settings.device_conf)
        self.gen_sh.gen_sh(self.settings.paths['hd']['sh'])
