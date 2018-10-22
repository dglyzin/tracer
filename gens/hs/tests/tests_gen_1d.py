from gens.hs.gen_env.gen_dim import GenD1
from gens.hs.gen_main import Gen

from settings.settings_main import Settings
from envs.hs.model.model_main import ModelNet as Model

from tests.tests_common import get_model_for_tests
from tests.tests_common import to_file, test_cpp

import os
import sys


def get_gen_1d(model='problems/test1d_two_blocks0',
               device_conf='default'):
    settings = Settings()
    gen = Gen(model, settings, device_conf)
    return(gen)


def test_gen_1d(model='problems/test1d_two_blocks0',
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
    settings = Settings(model, None, device_conf)
    # settings.make_all_pathes(model)
    # settings.set_device_conf(device_conf)

    gen = Gen(model, settings)
    gen.gen_all()
    gen.save_all()
    return(gen)


def test_gen_1d_old(model="tests/test1d_two_blocks0.json"):
    gen = GenD1(model)
    gen.gen_cpp()
    gen.gen_arrays()
    
    # save cpp:
    name = os.path.basename(model)
    cppFileName = to_file(gen.cpp_out, name)

    # save dom txt:
    folderName = cppFileName.split('.')[0]
    domFileName = folderName + '_dom.txt'

    gen.filler.save_txt(domFileName)

    # save dom bin:
    binFileName = folderName + '_bin.dom'
    gen.filler.save_bin(binFileName)

    return(os.path.basename(cppFileName))


if __name__ == '__main__':
    
    if '-t' in sys.argv:
        test_idx = sys.argv.index('-t') + 1
        test_name = os.path.join('problems', '1dTests',
                                 sys.argv[test_idx])
    else:
        test_name = 'problems/1dTests/Brusselator1d'
        # test_name = 'problems/1dTests/two_blocks0_delays'

    if '-d' in sys.argv:
        device_conf_idx = sys.argv.index('-d') + 1
        device_conf = sys.argv[device_conf_idx]
    else:
        device_conf = "default"

    test_gen_1d(test_name, device_conf)
