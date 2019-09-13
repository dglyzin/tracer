from gens.hs.gen_env.cpp.env.definitions.def_main import Gen as GenDef
from gens.hs.gen_env.cpp.env.params.params_main import Gen as GenParams

from gens.mini_solver.gen_equations import GenEqs
from gens.mini_solver.solver_render import GenCppRend


from gens.hs.fiocr.fiocr_main import Fiocr

import os


class Gen():
    def __init__(self, model, settings):
        # model="problems/2dTests/heat_block_1"
        self.params = Params()

        self.gen_eqs = GenEqs(self)

        # file io compilation routine:
        self.fiocr = Fiocr()

        self.model = model
        self.settings = settings if settings is not None else {}

    def set_params(self, funcIdxs, func_dict):
        '''
        Generate centrals for all equations systems from
        func_dict, bounds and vertexs optional.

        - ``func_dict`` -- dict like {sys_eq_num:
        {"system", [system equations]}}. if bound => has
        addition keys:
         btype, bound_values, side_num for bounds
         vertex_values, sides for vertexs.
        '''
        # convert eq strings to system
        # bound_values from func_dict
        # use GenCppCommon.parse_equations (it parse bound_values inside)
        # use GenCommon._get_eq_cpp for centrals
        # init values

        blockNumber = 0
        model = self.model
        params = self.params

        # out for definitions
        gen_def = GenDef()
        gen_def.params = params
        gen_def.common.set_params_for_definitions(self.model)

        # out for params:
        # gen_params = GenParams()
        # gen_params.cpp.set_params_for_parameters(self.model)

        # TODO: to gen equations.py
        self.gen_eqs.set_params_for_eqs(model, blockNumber, func_dict, params)

    def gen_src_files_cuda(self):

        if "hd_dir" in self.settings:
            hd_dir = self.settings["hd_dir"]
        else:
            hd_dir = os.getcwd()

        print("current path:")
        print(hd_dir)

        cppGen = GenCppRend(self, hd_dir=hd_dir)

        out_cuda = cppGen.get_out_for_mini_solver_cuda(self.params)
        path = os.path.join(hd_dir,
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cuda',
                            'core.cu')
        print("cuda path:")
        print(path)
        self.fiocr.to_file(out_cuda, path)

    def gen_src_files_cpp(self):

        # FOR src file generation
        if "hd_dir" in self.settings:
            hd_dir = self.settings["hd_dir"]
        else:
            hd_dir = os.getcwd()
        cppGen = GenCppRend(self, hd_dir=hd_dir)

        print("current path:")
        print(hd_dir)

        #    FOR cpp/include/core.h
        out_h = cppGen.get_out_for_mini_solver_cpp_core(self.params)

        path = os.path.join(hd_dir,
                            'solvers',
                            'mini_solver',
                            'cpp',
                            'include',
                            'core.h')
        print("core.h path:")
        print(path)
        self.fiocr.to_file(out_h, path)
        #    END FOR

        #    FOR cpp/kernels.cpp
        out_cpp = cppGen.get_out_for_mini_solver_cpp_kernels(self.params)

        path = os.path.join(hd_dir,
                            'solvers',
                            'mini_solver',
                            'cpp',
                            'kernels.cpp')
        print("kernels.cpp path:")
        print(path)
        self.fiocr.to_file(out_cpp, path)
        #    END FOR

        #    FOR cpp/solver.cpp
        out_cpp = cppGen.get_out_for_mini_solver_cpp_solver(self.params)

        path = os.path.join(hd_dir,
                            'solvers',
                            'mini_solver',
                            'cpp',
                            'solver.cpp')
        print("solver.cpp path:")
        print(path)
        self.fiocr.to_file(out_cpp, path)
        #    END FOR
        # END FOR


class Params():
    pass


if __name__ == "__main__":
    from envs.hs.model.model_main import ModelNet as Model
    model = Model()
    model.io.loadFromFile("problems/2dTests/heat_block_1")
    
    gen = Gen(model, None)
    gen.set_params(None,
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
    gen.gen_src_files_cpp()
