from ..block import Block
from ..equation import Equation
from ..model import Model
from ..funcGenerator import FuncGenerator
from generator1D import Generator1D, BlockInfo
import os
# from ...tests.introduction.part_2_2_gen_bouns import to_file


def test_gen_1D(modelFile="tests/short_restest_full.json"):
    model = get_model_for_tests(modelFile)
    g = Generator1D(model)
    bi = BlockInfo()
    block = g.blocks[0]
    bi.getBlockInfo(g, block, 0)

    outList = []
    outList.append(g.generateAllDefinitions())
    outList.append(g.generateInitials())

    ### central and bound func code here ###

    # outList.append(g.generateGetBoundFuncArray)
    out = reduce(lambda x, y: x+y, outList)
    
    to_file(out, 'from_test_gen_1D.cpp')
    return(g)


def get_model_for_tests(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def to_file(out, name='some_functions.cpp'):
    
    print("getcwd")
    print(os.getcwd())
    f = open(os.path.join(os.getcwd(), 'tests',
                          'introduction',
                          'src', name),
             'w')
    f.write(out)
    f.close()
