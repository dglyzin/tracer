from ..block import Block
from ..equation import Equation
from ..model import Model
from ..funcGenerator import FuncGenerator
from generator1D import Generator1D, BlockInfo
import os
# from ...tests.introduction.part_2_2_gen_bouns import to_file

from cppOutsForGenerators import CppOutsForGenerators as CppOutGen
from params import Params

from domainmodel.criminal.parser import Parser

import logging

# for independet launching this module
#logging.basicConfig(level=logging.DEBUG)

# create logger that child of tests.tester loger
logger = logging.getLogger('tests.tester.criminal.tests_gen')


def test_domain_1d(modelFile="tests/brusselator1d_bound_U.json"):
    model = get_model_for_tests(modelFile)
    params = Params()

    # for funcNamesStack and bounds and ics from params
    params.set_params_for_centrals(model)
    params.set_params_for_interconnects(model)
    params.set_params_for_bounds(model)

    # for namesAndNumbers
    params.set_params_for_array()

    params.set_params_for_dom_centrals(model)
    params.set_params_for_dom_interconnects()
    params.set_params_for_dom_bounds()
    
    return(params.functionMaps)


def test_templates_1d(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    Generate cpp for 1d.

    out will be in:
       'tests/introduction/src/from_test_template_1d.cpp'

    '''

    out = test_template_definitions(modelFile)
    out += test_template_initials(modelFile)
    out += test_template_params(modelFile)

    outl, params = test_template_centrals(modelFile)
    out += outl

    outl, params = test_template_interconnects(modelFile, params)
    out += outl

    outl, params = test_template_bounds(modelFile, params)
    out += outl
    out += test_template_array(modelFile, params)

    # print(out)

    to_file(out, 'from_test_template_1d.cpp')
    return(params)


def test_template_definitions(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    Generate cpp for centrals from
    template.

    template in :
       'criminal/templates/definitions.template'

    out will be in:
       'tests/introduction/src/from_test_template_definitions.cpp'

    '''
    model = get_model_for_tests(modelFile)

    params = Params()
    cppGen = CppOutGen()

    # parameters for definitions
    params.set_params_for_definitions(model)
    
    out = cppGen.get_out_for_definitions(params)

    to_file(out, 'from_test_template_definitions.cpp')

    return(out)


def test_template_array(modelFile="tests/brusselator1d_bound_U.json", params=None):
    '''
    DESCRIPTION:
    Generate cpp for centrals from
    template.

    After
     params.set_params_for_centrals
     params.set_params_for_interconnects
     params.set_params_for_bounds

    template in :
       'criminal/templates/array.template'

    out will be in:
       'tests/introduction/src/from_test_template_array.cpp'

    INPUT:
    params from central, interconnect, bounds
    '''
    #model = get_model_for_tests(modelFile)

    
    #if params is None:
    #    params = Params()

    cppGen = CppOutGen()

    # parameters for central
    #params.set_params_for_centrals(model)

    # parameters for bound
    #params.set_params_for_bounds(model)

    # parameters for interconnect
    #params.set_params_for_interconnects(model)

    params.set_params_for_array()
    out = cppGen.get_out_for_array(params)

    to_file(out, 'from_test_template_array.cpp')

    return(out)


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
    parser = Parser()
    
    # parameters for central
    params.set_params_for_centrals(model)
    
    parser.params.diffType = 'pure'
    parser.params.diffMethod = 'common'
    parser.params.parameters = model.params
    parser.params.parametersVal = model.paramValues[0]
    
    for eq in params.equations:
        parser.params.blockNumber = eq.blockNumber
        eq.parsedValues = [parser.parseMathExpression(value)
                           for value in eq.values]
    out = cppGen.get_out_for_centrals(params)
    
    to_file(out, 'from_test_template_centrals.cpp')

    return((out, params))

    
def test_template_interconnects(modelFile="tests/1dTests/test1d_three_blocks0.json", params=None):
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
    
    if params is None:
        params = Params()

    cppGen = CppOutGen()
    parser = Parser()

    # parameters for interconnect
    params.set_params_for_interconnects(model)

    parser.params.diffType = 'pure'
    # TODO for diffMethod
    # in 2d We should use diff instead diff_interconnect
    # or choice between special and common in action_for_termDiff
    # or in derivCodeGenerator.__init__
    parser.params.diffMethod = 'interconnect'
    parser.params.parameters = model.params
    parser.params.parametersVal = model.paramValues[0]
    
    for ic in params.ics:
        parser.params.blockNumber = ic.blockNumber
        parser.params.side = ic.side
        parser.params.firstIndex = ic.firstIndex
        parser.params.secondIndexSTR = ic.secondIndex
        print(ic.equation)
        
        ic.parsedValues = [parser.parseMathExpression(eq)
                           for eq in ic.equation.system]
    out = cppGen.get_out_for_interconnects(params)
    
    to_file(out, 'from_test_template_interconnects.cpp')

    return((out, params))


def test_template_bounds(modelFile="tests/brusselator1d_bound_U.json", params=None):
    '''
    DESCRIPTION:
    Generate cpp for bounds from
    template.

    It always placed after test_template_interconnects
    because if interconnect exist for some side then
    ignore it bound.

    template in :
       'criminal/templates/bound_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_bounds.cpp'

    INPUT:
    param from test_template_interconnects
    '''
    model = get_model_for_tests(modelFile)

    if params is None:
        params = Params()

    cppGen = CppOutGen()
    parser = Parser()

    # parameters for bound
    params.set_params_for_bounds(model)
    
    for bound in params.bounds:
        if bound.btype == 0:
            # Dirichlet
            bound.parsedValues = bound.values
        else:
            # Neuman
            parser.params.diffType = 'pure'
            # TODO for diffMethod
            # in 2d We should use diff instead diff_special
            # or choice between special and common in action_for_termDiff
            # or in derivCodeGenerator.__init__
            parser.params.diffMethod = 'special'
            parser.params.parameters = model.params
            parser.params.parametersVal = model.paramValues[0]

            parser.params.blockNumber = bound.blockNumber
            parser.params.side = bound.side

            # bound can be U(t-1, {x, 0.3})
            # so dim and shape needed
            # TODO: for dim
            parser.params.dim = '1D'
            cellSize = 1
            parser.params.shape = [cellSize/float(model.gridStepX),
                                   cellSize/float(model.gridStepY),
                                   cellSize/float(model.gridStepZ)]
            bound.parsedValues = []

            # for derivOrder = 1:
            # du/dx = bound.value[i]
            # for derivOrder = 2:
            # left border
            # ddu/ddx = 2*(u_{1}-u_{0}-dy*bound.value[i])/(dx^2)
            # right border
            # ddu/ddx = 2*(u_{n-1}-u_{n}-dy*bound.value[i])/(dx^2)
            for i, eq in enumerate(bound.equation.system):
                # parse phi
                value = parser.parseMathExpression(bound.values[i])
                parser.cppOut.dataTermMathFuncForDiffSpec = value
                # parse eq(phi)
                bound.parsedValues.append(parser.parseMathExpression(eq))

    out = cppGen.get_out_for_bounds(params)
    
    to_file(out, 'from_test_template_bounds.cpp')

    return((out, params))


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

    return(out)


def test_template_initials(modelFile="tests/short_restest_full.json"):
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
    parser = Parser()

    model = get_model_for_tests(modelFile)
    params.set_params_for_initials(model)

    # FOR PARSER
    parser.params.parameters = model.params
    parser.params.parametersVal = model.paramValues[0]
    
    # TODO: sin(x)->sin(idxX + Block0OffsetX * DXM1)
    for blockNumber, block in enumerate(params.blocks):

        # FOR initial
        for initial in block.initials:
            initial.parsedValues = initial.values
        # END FOR

        # FOR Dirichlet
        parser.params.blockNumber = blockNumber
        parser.params.dim = '1D'
        cellSize = 1
        parser.params.shape = [cellSize/float(model.gridStepX),
                               cellSize/float(model.gridStepY),
                               cellSize/float(model.gridStepZ)]
        for bound in block.bounds:
            bound.parsedValues = [parser.parseMathExpression(value)
                                  for value in bound.values]
        # END FOR
    # END FOR PARSER

    out = cppGen.get_out_for_initials(params)
    to_file(out, 'from_test_template_initials.cpp')

    return(out)


def test_gen_1D(modelFile="tests/brusselator1d_bound_U.json"):
    model = get_model_for_tests(modelFile)
    g = Generator1D(model)
    bi = BlockInfo()
    block = g.blocks[0]

    bi.getBlockInfo(g, block, 0)

    outList = []
    return(g.generateAllDefinitions())

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
