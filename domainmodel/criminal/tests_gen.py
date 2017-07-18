from ..block import Block
from ..equation import Equation
from ..model import Model
from ..funcGenerator import FuncGenerator
from generator1D import Generator1D, BlockInfo
import os
# from ...tests.introduction.part_2_2_gen_bouns import to_file

from cppOutsForGenerators import CppOutsForGenerators as CppOutGen
from params import Params


def test_template_centrals(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    Generate cpp for centrals from
    template.

    template in :
       'criminal/templates/central_functions.template'

    out will be in:
       'tests/introduction/src/from_test_template_centrals.cpp'

    '''
    model = get_model_for_tests(modelFile)
    
    params = Params()
    cppGen = CppOutGen()

    # parameters for bound
    params.set_params_for_centrals(model)
    out = cppGen.get_out_for_centrals(params)
    
    to_file(out, 'from_test_template_centrals.cpp')


def test_template_interconnects(modelFile="tests/1dTests/test1d_three_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for interconnects from
    template.

    template in :
       'criminal/templates/interconnects.template'

    out will be in:
       'tests/introduction/src/from_test_template_interconnects.cpp'

    '''
    model = get_model_for_tests(modelFile)
    
    params = Params()
    cppGen = CppOutGen()

    # parameters for bound
    params.set_params_for_interconnects(model)
    out = cppGen.get_out_for_interconnects(params)
    
    to_file(out, 'from_test_template_interconnects.cpp')


def test_template_bounds(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    Generate cpp for bounds from
    template.

    template in :
       'criminal/templates/bound_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_bounds.cpp'
    '''
    model = get_model_for_tests(modelFile)
    g = Generator1D(model)
    bi = BlockInfo()
    block = g.blocks[0]
    bi.getBlockInfo(g, block, 0)
    
    params = Params()
    cppGen = CppOutGen()

    # parameters for bound
    params.set_params_for_bounds(model)
    out = cppGen.get_out_for_bounds(params)
    
    to_file(out, 'from_test_template_bounds.cpp')

    return(bi)


def test_template_params(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    Generate cpp for params from
    template.

    template in :
       'criminal/templates/params.template'

    out will be in:
       'tests/introduction/src/from_test_template_params.cpp'
    '''
    params = Params()
    cppGen = CppOutGen()

    model = get_model_for_tests(modelFile)
    params.set_params_for_parameters(model)
    out = cppGen.get_out_for_parameters(params)
    to_file(out, 'from_test_template_params.cpp')


def test_template_initial(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    Generate cpp for initial and Dirichlet from
    template example.

    template in :
       'criminal/templates/initial_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_initial.cpp'
    '''
    params = Params()
    cppGen = CppOutGen()

    model = get_model_for_tests(modelFile)
    params.set_params_for_initials(model)
    out = cppGen.get_out_for_initials(params)
    to_file(out, 'from_test_template_initial.cpp')


def test_gen_1D(modelFile="tests/brusselator1d_bound_U.json"):
    model = get_model_for_tests(modelFile)
    g = Generator1D(model)
    bi = BlockInfo()
    block = g.blocks[0]

    bi.getBlockInfo(g, block, 0)

    outList = []

    '''
    PARAMS FOR generateAllDefinitions
    gen.gridStep
    gen.defaultIndepVars = ['x', 'y', 'z']
    gen.allBlockSizeLists = [[Block0SizeX, Block0SizeY, Block0SizeZ],
                             [Block1SizeX, Block1SizeY, Block1SizeZ]},
                             ...]
    gen.allBlockOffsetList = [[Block0OffsetX, Block0OffsetY, Block0OffsetZ],
                              [Block1OffsetX, Block1OffsetY, Block1OffsetZ],
                              ...]
    gen.cellsizeList = [Block0CELLSIZE, Block1CELLSIZE, ...]
    '''
    # outList.append(g.generateAllDefinitions())
    # outList.append(g.generateInitials())

    ### central and bound func code here ###
    '''
    for blockNumber, block in enumerate(self.generator.blocks):
        systemsForCentralFuncs, numsForSystems, totalBCondLst, totalInterconnectLst, blockFunctionMap = self.generator.getBlockInfo(block, blockNumber)
        cf, arrWithFunctionNames = self.generator.generateCentralFunctionCode(block, blockNumber, systemsForCentralFuncs, numsForSystems)

        bf = self.generator.generateBoundsAndIcs(block, blockNumber, arrWithFunctionNames, blockFunctionMap, totalBCondLst, totalInterconnectLst)
            
        totalArrWithFunctionNames.append(arrWithFunctionNames)
        functionMaps.append(blockFunctionMap)
    '''

    # arrWithFunctionNames from central and bound
    # outList.append(g.generateGetBoundFuncArray(arrWithFunctionNames))
    # out = reduce(lambda x, y: x+y, outList)
    # to_file(out, 'from_test_gen_1D.cpp')
    return(g)


def get_model_for_tests(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def to_file(out, name='some_functions.cpp'):
    
    path = os.path.join(os.getcwd(), 'tests',
                        'introduction',
                        'src', name)
    print("path =")
    print(path)
    f = open(path, 'w')
    f.write(out)
    f.close()
