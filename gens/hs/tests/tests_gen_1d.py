from gens.hs.gen_1d import GenD1
from tests.tests_common import get_model_for_tests
from tests.tests_common import to_file, test_cpp

import os


def test_gen_1d(model="tests/test1d_two_blocks0.json"):
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
    binFileName = folderName + '_bin'
    gen.filler.save_bin(binFileName)

    return(os.path.basename(cppFileName))
