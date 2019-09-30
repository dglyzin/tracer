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

    def set_params(self, eqs_dict, bs_dict, funcIdxs):
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

        funcIdxs, eqs_dict, bs_dict = self.gen_eqs.fix_indexes(funcIdxs, eqs_dict, bs_dict)
        print("new_funcIdxs:")
        print(funcIdxs)
        print("eqs_dict:")
        print(eqs_dict)
        print("bs_dict:")
        print(bs_dict)
        self.gen_eqs.set_params_for_eqs(model, blockNumber,
                                        eqs_dict, params)

        bs_sides = self.gen_eqs.create_bs_sides(funcIdxs)
        print("bs_sides:")
        print(bs_sides)
        self.gen_eqs.set_params_for_bounds(model, blockNumber,
                                           eqs_dict,
                                           bs_dict, bs_sides,
                                           params)
        print("apply_postproc:")
        self.gen_eqs.apply_postproc(params)

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
    '''
    from scipy.misc import imread
    from scipy.misc import imsave
    import base64

    # save img data:
    with open(node_img_file, "wb") as f:
        # imsave(img_orign, node_img_file, format='jpeg')
        f.write(base64.decodebytes(img_orign.encode("utf-8")))
        # f.write(base64.decodebytes(node_data_img.encode("utf-8")))
    img = imread(node_img_file, mode="L")
    '''
    import numpy as np
    bimg = np.zeros((10, 10))
    
    # side 2:
    bimg[0, 3:7] = 135
    bimg[0, 7:9] = 183

    # side 3:
    bimg[9, 1:5] = 73
    bimg[9, 5:7] = 164

    # side 0:
    bimg[1:9, 0] = 164

    # side 1:
    bimg[1:7, 9] = 183
    bimg[7:9, 9] = 183

    # inner borders:
    bimg[3, 3] = 75
    bimg[3, 4] = 164
    bimg[4, 3] = 75
    bimg[4, 4] = 164

    img = img.astype(np.int)

    # bs_sides = {0: [0, 164], 1: [0, 183],
    #             2: [0, 135, 183], 3: [0, 73, 164]}

    bounds = {
        0: {"system": ["0.1"], "btype": 0},
        164: {"system": ["sin(x)"], "btype": 1, "side_num": 1},
        183: {"system": ["cos(x)"], "btype": 1, "side_num": 1},
        135: {"system": ["exp(x)"], "btype": 1, "side_num": 1},
        73: {"system": ["sqrt(x)"], "btype": 1, "side_num": 1}}

    equations = {
        0: {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"]},
        75: {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"]},
        164: {"system": ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])"]}}
    print("img array:")
    print(img)

    model = Model()
    model.io.loadFromFile("problems/2dTests/heat_block_1")

    gen = Gen(model, None)
    gen.set_params(equations, bounds, img)
    '''
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
    '''
    # gen.gen_src_files_cpp()
    print("namesAndNumbers:")
    print(gen.params.namesAndNumbers)

    print("functionMap:")
    print(gen.params.functionMap)
