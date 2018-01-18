'''
/hybriddomain$ python3 -m domainmodel.criminal.test_mini_solver

'''
import os

from domainmodel.criminal.parser import Parser
from domainmodel.criminal.cppOutsForGenerators import CppOutsForGenerators as CppOutGen
from domainmodel.criminal.params import Params

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pchs

import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.model import Model
    import domainmodel.criminal.mini_solver.main as mn
else:
    from ..model import Model
    import mini_solver.main as mn


def test_solver_cpp(modelFile="tests/2dTests/test2d_for_intervals_single.json",
                    cuda=False):

    # FOR get model
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile
    # END FOR

    # FOR set params
    params = Params()

    params.set_params_for_definitions(model)

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
    # END FOR

    # FOR parser
    parser = Parser()

    # FOR kernels equations for centrals
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
            eq.parsedValues = [parser.parseMathExpression(value)
                               for value in eq.values]
    # END FOR

    # FOR kernels equations for bound
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
            print("PARAMETERS")
            print(parser.cppOut.params.parameters)
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
    # END FOR

    # remove vertex
    names = params.namesAndNumbers[0]
    _test = ['Vertex' not in name for name in names]
    params.namesAndNumbers[0] = [name for i, name in enumerate(names)
                                 if _test[i]]

    # FOR src file generation
    cppOut = CppOutGen()

    if cuda:
        out_cuda = cppOut.get_out_for_mini_solver_cuda(params)
        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cuda',
                            'core.cu')
        to_file(out_cuda, path)
    else:
        #    FOR cpp/include/core.h
        out_h = cppOut.get_out_for_mini_solver_cpp_core(params)

        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cpp',
                            'include',
                            'core.h')

        to_file(out_h, path)
        #    END FOR

        #    FOR cpp/kernels.cpp
        out_cpp = cppOut.get_out_for_mini_solver_cpp_kernels(params)

        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cpp',
                            'kernels.cpp')

        to_file(out_cpp, path)
        #    END FOR
    # END FOR

    # FOR prepare data to solver:
    #    FOR getting input parameters
    funcInit = params.fill_2d_init_funcs(model)

    functionMap = params.functionMaps[0]
    funcIdxs = params.fill_2d_func_idxs(model, functionMap)

    funcIdxs_file = os.path.join(os.getcwd(),
                                 'domainmodel',
                                 'criminal',
                                 'mini_solver',
                                 'funcIdxs_file.txt')
    with open(funcIdxs_file, 'w') as f:
        f.write(str(list(funcIdxs)))

    parameters = params.fill_parameters(model)
    
    print("parameters")
    print(parameters)
    
    print("params.functionMaps")
    print(params.functionMaps[0])
    #    END FOR
    
    mn.Block0CountY, mn.Block0CountX = funcInit.shape
    mn.SIZE_OF_RESULT = mn.Block0CountX * mn.Block0CountY

    COUNT_OF_DELAYS = 1
    ITERATION_COUNT = 2

    result = np.zeros((mn.Block0CountY, mn.Block0CountX)).astype('double')
    result[:] = funcInit[:]
    result.astype('double')

    source = np.zeros((COUNT_OF_DELAYS, mn.Block0CountY, mn.Block0CountX)).astype('double')
    source[0][:] = funcInit[:]
    source = source.astype('double')

    funcIdxs = funcIdxs.astype('int32')

    parameters = parameters.astype('double')

    # interconnect dont used now
    ic = np.zeros((1)).astype('double')
    # END FOR

    # FOR compilation
    curDir = os.getcwd()
    path = os.path.join(curDir,
                        'domainmodel',
                        'criminal',
                        'mini_solver')
    if cuda:
        mn.compile_cuda(path, 1)
    else:
        mn.compile_cpp(path, 1)
    # END FOR

    # main code
    mn.solver(funcIdxs, result, source, parameters, ic,
              ITERATION_COUNT, path, cuda)

    _plt = mn.plot(result)
    _plt.show()
    print("result")
    print(result)
    # return(funcInit)
    return(result)


def get_model_for_tests(modelFile="tests/2dTests/test2d_for_intervals_single.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def to_file(out, path):
    
    '''
    path = os.path.join(os.getcwd(),
                        'domainmodel',
                        'criminal',
                        'mini_solver',
                        name)
    '''
    print("path =")
    print(path)
    f = open(path, 'w')
    f.write(out)
    f.close()


if __name__ == '__main__':
    cuda = True
    test_solver_cpp(cuda=cuda)
