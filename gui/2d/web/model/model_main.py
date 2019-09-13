import os
import sys
import inspect

# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
gui = currentdir.find("gui")

hd_dir = currentdir[:gui]
print(hd_dir)
if hd_dir not in sys.path:
    sys.path.insert(0, hd_dir)

from gens.mini_solver.gen_main import Gen


class Model():
    def __init__(self):
        
        from envs.hs.model.model_main import ModelNet as Model
    
        model = Model()
        model_path = os.path.join(hd_dir,
                                  "problems/2dTests/heat_block_1")
        model.io.loadFromFile(model_path)
        self.genSrc = Gen(model, {"hd_dir": hd_dir})

    def gen_src(self):

        '''TODO: make model_path as param
        make func_dict as param
        sinch funcIdxs with namesAndNumbers'''

        self.genSrc.set_params(None,
                               {0:
                                {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"]},
                                1:
                                {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"],
                                 "btype": 0,
                                 "bound_values": ["0.0"],
                                 "side_num": 0},
                                2: {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"],
                                    "btype": 0,
                                    "bound_values": ["0.1"],
                                    "side_num": 0,
                                    "vertex_values": ["0.2"],
                                    "sides": [0, 0]}})
        self.genSrc.gen_src_files_cpp()


if __name__ == "__main__":
    
    model = Model()
    model.gen_src()
