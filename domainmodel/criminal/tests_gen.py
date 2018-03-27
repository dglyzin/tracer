import os
# from ...tests.introduction.part_2_2_gen_bouns import to_file

from domainmodel.criminal.parser import Parser

import matplotlib.pyplot as plt
import matplotlib.patches as pchs

import sys
# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.block import Block
    from domainmodel.equation import Equation
    from domainmodel.model import Model
    from domainmodel.funcGenerator import FuncGenerator
    from domainmodel.criminal.generator1D import Generator1D, BlockInfo
    from domainmodel.criminal.cppOutsForGenerators import CppOutsForGenerators as CppOutGen
    from domainmodel.criminal.params import Params
else:
    from ..block import Block
    from ..equation import Equation
    from ..model import Model
    from ..funcGenerator import FuncGenerator
    from generator1D import Generator1D, BlockInfo
    from cppOutsForGenerators import CppOutsForGenerators as CppOutGen
    from params import Params

#import logging

# for independet launching this module
#logging.basicConfig(level=logging.DEBUG)

# create logger that child of tests.tester loger
#logger = logging.getLogger('tests.tester.criminal.tests_gen')


def test_domain_2d(modelFile="tests/2dTests/test2d_for_intervals_single_delay.json"):
    
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    params = Params()

    # for funcNamesStack and bounds and ics from params
    params.set_params_for_centrals(model)
    
    params.set_params_for_bounds_2d(model)

    # for namesAndNumbers
    params.set_params_for_array()

    params.set_params_for_dom_centrals(model)
    try:
        params.set_params_for_dom_interconnects()
    except:
        pass

    params.set_params_for_dom_bounds(model)
    
    out = str(params.functionMaps)
    to_file(out, "from_test_domain_2d.txt")

    return(params.functionMaps)


def test_domain_1d(modelFile="tests/brusselator1d_bound_U.json"):
    
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
    params = Params()

    # for funcNamesStack and bounds and ics from params
    params.set_params_for_centrals(model)
    params.set_params_for_interconnects(model)
    params.set_params_for_bounds(model)

    # for namesAndNumbers
    params.set_params_for_array()
    # return(params)
    params.set_params_for_dom_centrals(model)
    params.set_params_for_dom_interconnects()
    params.set_params_for_dom_bounds(model)

    out = str(params.functionMaps)
    to_file(out, "from_test_domain_1d.txt")

    return(params.functionMaps)


def test_templates_2d(modelFile="tests/2dTests/test2d_for_intervals_single_delay.json"):
    '''
    DESCRIPTION:
    Generate cpp for 2d.
    Single block only (without interconnects)

    out will be in:
       'tests/introduction/src/from_test_template_2d.cpp'

    '''

    out = test_template_definitions(modelFile)
    out += test_template_initials(modelFile, dim=2)
    out += test_template_params(modelFile)

    outl, params = test_template_centrals(modelFile)
    out += outl

    # outl, params = test_template_interconnects(modelFile, params)
    # out += outl

    outl, params = test_template_bounds_2d(modelFile, params)
    out += outl
    out += test_template_array(params)

    out = params.postprocessing(out)
    params.out = out

    to_file(out, 'from_test_template_2d.cpp')
    return(params)


def test_template_bounds_2d(modelFile="tests/2dTests/test2d_for_intervals_single.json", params=None):
    '''
    DESCRIPTION:
    Generate cpp for bounds 2d from
    template.

    It always placed after test_template_interconnects
    because if interconnect exist for some side then
    ignore it bound.

    template in :
       'criminal/templates/bound_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_bounds_2d.cpp'

    INPUT:
    param from test_template_interconnects
    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)

    if params is None:
        params = Params()
        dataTermVarsForDelay = None
    else:
        # for delays from other templates
        try:
            dataTermVarsForDelay = params.dataTermVarsForDelay
        except:
            dataTermVarsForDelay = None

    cppGen = CppOutGen()
    parser = Parser()

    # for delays
    if dataTermVarsForDelay is not None:
        parser.cppOut.dataTermVarsForDelay = dataTermVarsForDelay

    # parameters for bound
    params.set_params_for_bounds_2d(model)

    # FOR PLOT:
    
    # init plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scale = 10
    # draw block
    block = model.blocks[-1]

    width_x = block.sizeX * scale
    height_y = block.sizeY * scale

    orign_x = 0
    orign_y = -height_y

    r = pchs.Rectangle((orign_x, orign_y), width=width_x, height=height_y,
                       color='red', alpha=0.4)
    ax.add_patch(r)
    color = 0.1

    # FOR draw equation regions
    for eRegion in block.equationRegions:

        width_x = eRegion.xto-eRegion.xfrom
        width_x = width_x * scale

        height_y = eRegion.yto-eRegion.yfrom
        height_y = height_y * scale

        orign_x = eRegion.xfrom
        orign_x = orign_x * scale

        orign_y = -eRegion.yfrom * scale - height_y

        equation_text = 'e %s' % str(eRegion.equationNumber)
        # equation_text = model.equations[eRegion.equationNumber].system

        # add rectangle at scen
        ax.add_patch(
            pchs.Rectangle((orign_x, orign_y),
                           width=width_x, height=height_y,
                           color=[0.1, 0.1, color], alpha=0.4))

        # add equation text
        plt.annotate(equation_text,
                     xy=(orign_x + width_x/2.0,
                         orign_y + height_y/2.0))
        if color < 1:
            color += 0.1
    # END FOR

    # FOR draw sides
    color = 0.0
    side_border = 3.0
    for side in params.new_sides:
        # for last block
        if side['blockNumber'] == model.blocks.index(block):
            _block = model.blocks[side['blockNumber']]
            for interval in side['side_data']:

                # default text
                equation_text = str(interval.name)

                if side['side'] == 0:

                    width_x = side_border

                    height_y = interval[1] - interval[0]
                    height_y = height_y * scale

                    orign_x = -side_border

                    orign_y = -interval[0] * scale - height_y

                if side['side'] == 1:

                    width_x = side_border
                    height_y = interval[1] - interval[0]
                    height_y = height_y * scale
                    orign_x = _block.sizeX * scale
                    orign_y = -interval[0] * scale - height_y

                if side['side'] == 2:

                    width_x = interval[1] - interval[0]
                    width_x = width_x * scale
                    height_y = side_border
                    orign_x = interval[0] * scale
                    orign_y = 0
                    
                    equation_text = 'b: %s \n' % str(interval.name['b'])
                    equation_text += 'e: %s' % str(interval.name['e'])

                if side['side'] == 3:

                    width_x = interval[1] - interval[0]
                    width_x = width_x * scale
                    height_y = side_border
                    orign_x = interval[0] * scale
                    orign_y = -_block.sizeY * scale - side_border
                    
                    equation_text = 'b: %s \n' % str(interval.name['b'])
                    equation_text += 'e: %s' % str(interval.name['e'])

                if color < 1.0:
                    color += 0.05

                # add rectangle at scen
                ax.add_patch(
                    pchs.Rectangle((orign_x, orign_y),
                                   width=width_x, height=height_y,
                                   color=[0.3, 0.3, color], alpha=0.4))
                # add equation text
                plt.annotate(equation_text,
                             xy=(orign_x + width_x/2.0,
                                 orign_y + height_y/2.0))
    # END FOR

    # FOR draw vertex
    
    vertex_border = 1.0
    for vertex in params.bounds_vertex:
        # for last block
        if vertex.blockNumber == model.blocks.index(block):
            _block = model.blocks[vertex.blockNumber]

            if vertex.sides == [0, 2]:
                orign_x = -side_border
                orign_y = side_border
            elif(vertex.sides == [2, 1]):
                orign_x = _block.sizeX * scale + side_border/2.0
                orign_y = side_border
            elif(vertex.sides == [1, 3]):
                orign_x = _block.sizeX * scale + side_border
                orign_y = -_block.sizeY * scale - 3.7*side_border

            elif(vertex.sides == [3, 0]):
                orign_x = - side_border
                orign_y = -_block.sizeY * scale - 3.7*side_border

            equation_text = 'v: %s \n' % str(vertex.sides)
            equation_text += 'b: %s \n' % str(vertex.boundNumber)
            equation_text += 'e: %s' % str(vertex.equationNumber)

            # add equation text
            plt.annotate(equation_text,
                         xy=(orign_x,
                             orign_y))
    # END FOR

    plt.xlim(-2*side_border, block.sizeX*scale+2*side_border)
    plt.ylim(-block.sizeY*scale-4.5*side_border, 0+side_border)
    
    plt.annotate('$ \omega= \leq = \{(x,y)|x\leq y\}$',
                 xy=(4, 7))

    path = os.path.join(os.getcwd(), 'tests',
                        'introduction',
                        'src',
                        'from_test_template_bounds_2d.png')
    print("path")
    print(path)
    plt.savefig(path)
    # END FOR

    # parse for sides:
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
            parser.params.dim = '2D'
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

    # parse for vertex:
    for bound in params.bounds_vertex:
        
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
            parser.params.diffMethod = 'vertex'
            parser.params.parameters = model.params
            parser.params.parametersVal = model.paramValues[0]

            parser.params.blockNumber = bound.blockNumber
            parser.params.vertex_sides = bound.sides

            # bound can be U(t-1, {x, 0.3})
            # so dim and shape needed
            # TODO: for dim
            parser.params.dim = '2D'
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

    out_bounds = cppGen.get_out_for_bounds(params)
    out_vertex = cppGen.get_out_for_vertex_2d(params)

    to_file(out_bounds, 'from_test_template_bounds_2d.cpp')
    to_file(out_vertex, 'from_test_template_vertex_2d.cpp')

    out = out_bounds
    out += out_vertex

    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

    return((out, params))

    
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
    out += test_template_array(params)

    # print(out)
    
    out = params.postprocessing(out)

    params.out = out
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
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)

    params = Params()
    cppGen = CppOutGen()

    # parameters for definitions
    params.set_params_for_definitions(model)
    
    out = cppGen.get_out_for_definitions(params)

    to_file(out, 'from_test_template_definitions.cpp')

    return(out)


def test_template_array(params=None):
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
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
    
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
        print("eq.values")
        print(eq.values)
        parser.params.blockNumber = eq.blockNumber
        if eq.cpp:
            eq.parsedValues = eq.values
        else:
            #TODO parser
            eq.parsedValues = [value  # parser.parseMathExpression(value)
                               for value in eq.values]
        '''
        print("eq.values")
        print(eq.values)
        parser.params.blockNumber = eq.blockNumber
        eq.parsedValues = [parser.parseMathExpression(value)
                           for value in eq.values]
        '''
    out = cppGen.get_out_for_centrals(params)
    
    to_file(out, 'from_test_template_centrals.cpp')

    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

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
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
    
    if params is None:
        params = Params()
    else:
        # for delays from other templates
        try:
            dataTermVarsForDelay = params.dataTermVarsForDelay
        except:
            dataTermVarsForDelay = None

    cppGen = CppOutGen()
    parser = Parser()

    # for delays
    if dataTermVarsForDelay is not None:
        parser.cppOut.dataTermVarsForDelay = dataTermVarsForDelay

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

    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

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
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)

    if params is None:
        params = Params()
    else:
        # for delays from other templates
        try:
            dataTermVarsForDelay = params.dataTermVarsForDelay
        except:
            dataTermVarsForDelay = None

    cppGen = CppOutGen()
    parser = Parser()

    # for delays
    if dataTermVarsForDelay is not None:
        parser.cppOut.dataTermVarsForDelay = dataTermVarsForDelay

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
                ### bound.parsedValues.append(parser.parseMathExpression(eq))
                # TODO parser
                bound.parsedValues.append(eq)

    out = cppGen.get_out_for_bounds(params)
    
    to_file(out, 'from_test_template_bounds.cpp')
    
    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

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

    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
    params.set_params_for_parameters(model)
    out = cppGen.get_out_for_parameters(params)
    to_file(out, 'from_test_template_params.cpp')

    return(out)


def test_template_initials(modelFile="tests/short_restest_full.json", dim=1):
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

    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
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
        parser.params.dim = '%sD' % str(dim)
        cellSize = 1
        parser.params.shape = [cellSize/float(model.gridStepX),
                               cellSize/float(model.gridStepY),
                               cellSize/float(model.gridStepZ)]
        for bound in block.bounds:
            bound.parsedValues = [parser.parseMathExpression(value)
                                  for value in bound.values]
        # END FOR
    # END FOR PARSER
    
    params.dim = dim
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
