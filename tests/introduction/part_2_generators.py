'''
DESCRIPTION:
Some functions for understanding how
generators of .cpp code work.

From most general to particlular.

SHEME OF ABSTRACTIONs:
model.createCPPandGetFunctionMaps
uses
   FuncGenerator.generateAllFunctions
        from funcGenerator.py
   uses
      AbstractGenerator.generateCentralFunctionCode
         from abstractGenerator.py
      uses
         MathExpressionParser.parseMathExpression
          from equationParser.py
         and
         RHSCodeGenerator.generateRightHandSideCode{..Delay}
          from rhsCodeGenerator.py
'''
from domainmodel.block import Block
from domainmodel.equation import Equation
from domainmodel.model import Model
from domainmodel.funcGenerator import FuncGenerator
from domainmodel.generator2D import Generator2D
from domainmodel.abstractGenerator import AbstractGenerator


def get_gen_for_test(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What is generator.
    Create generator for all tests.

    EXAMPLE:
    "tests/brusselator1d_bound_U.json"
    '''
    # load model
    model = get_model_for_tests(modelFile)

    gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]
    haloSize = model.getHaloSize()
    mDO = model.getMaxDerivOrder()
    delay_lst = model.determineDelay()

    print("delay_lst = ")
    print(delay_lst)
    
    gen = FuncGenerator(delay_lst, mDO, haloSize, model.equations,
                        model.blocks, model.initials, model.bounds,
                        model.interconnects, gridStep, model.params,
                        model.paramValues, model.defaultParamsIndex,
                        preprocessorFolder="some_folder")
    return(gen)


def get_model_for_tests(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def test_model_create_cpp():
    '''
    DESCRIPTION:
    How .json become .cpp.
    .json = "hybriddomain/tests/short_restest_delay.json"
    .cpp =  "hybriddomain/tests/introduction/src/
                from_model_createCPP.cpp"
    '''
    
    # load model
    model = get_model_for_tests()
    model.createCPPandGetFunctionMaps(
        "tests/introduction/src/from_model_createCPP.cpp",
        "prepr_folder_path")
    return(model)


def test_func_gen():
    '''
    DESCRIPTION:
    What is funcGenerator.
    
    '''

    # load gen
    gen = get_gen_for_test()

    outputStr, functionMaps = gen.generateAllFunctions()

    return(outputStr, functionMaps)
