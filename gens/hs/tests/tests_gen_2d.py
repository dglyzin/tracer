# python3 -m gens.hs.tests.tests_gen_2d
from gens.hs.gen_env.gen_dim import GenD2
from gens.hs.gen_main import Gen

from settings.settings_main import Settings
from envs.hs.model.model_main import ModelNet as Model

from tests.tests_common import get_model_for_tests
from tests.tests_common import to_file, test_cpp

import os
import sys


def test_gen_2d(model='problems/2dTests/tests_2d_two_blocks0',
                device_conf='default'):

    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    print("model:")
    print(model.base.projectName)

    # settings:
    settings = Settings()
    settings.make_all_pathes(model)
    settings.set_device_conf(device_conf)

    gen = Gen(model, settings)
    gen.gen_all()
    gen.save_all()
    return(gen)


def test_gen_dim_2d(model=('problems/2dTests/tests_2d_two_blocks0')):
    
    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    class TmpNet():
        pass
    tmp_net = TmpNet()
    tmp_net.model = model

    gen_dim = GenD2(tmp_net)
    gen_dim.gen_cpp()
    gen_dim.gen_dom()
    
    # print("cpp_out")
    # print(gen_dim.cpp_out)

    print("\nnamesAndNumbers:")
    print(gen_dim.namesAndNumbers)

    print("\nfucntionMaps:")
    print(gen_dim.functionMaps)

    return(gen_dim)


if __name__ == '__main__':
    
    test_gen_2d()
    # test_gen_dim_2d()
