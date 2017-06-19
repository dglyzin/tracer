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


def get_model_for_tests(modelFile="tests/short_restest_delay.json"):
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

    # load model
    model = get_model_for_tests()

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
    
    outputStr, functionMaps = gen.generateAllFunctions()

    return(outputStr, functionMaps)


# equation for test_gen_central
e = Equation("test")
e.vars = [u'x', u'y']
e.system = [u"U'=a*(D[U(t-1),{y,2}])"]


def test_gen_central(eqList=[e]):
    '''
    DESCRIPTION:
    Generate central function .cpp code
    for equation in eqList.
    '''

    # load template model
    model = get_model_for_tests()

    # ?
    gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]
    haloSize = model.getHaloSize()
    mDO = 3
    delay_lst = []

    gen = AbstractGenerator(delay_lst, mDO, haloSize, model.equations,
                            model.blocks, model.initials, model.bounds,
                            model.interconnects, gridStep, model.params,
                            model.paramValues, model.defaultParamsIndex)
    
    out = []
    for i in range(len(eqList)):
        out.append("For equation: \n")
        out.append(eqList[i].system[0])
        out.append("\n")
        out.append("result: ")
        out.append("\n")
        fn, _ = gen.generateCentralFunctionCode("", i, [eqList[i]], [i])
        out.append(fn)

    out.append("\n \n")
    return(''.join(out))


def test_gen_2D():
    '''
    DESCRIPTION:
    What is Generator2D
    and
    how its work.
    At generateCentralFunctionCode example.
    '''
    # load model
    model = get_model_for_tests()

    # ?
    gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]
    haloSize = model.getHaloSize()
    mDO = model.getMaxDerivOrder()
    delay_lst = model.determineDelay()

    # ge
    generator = Generator2D(delay_lst, mDO, haloSize, model.equations,
                            model.blocks, model.initials, model.bounds,
                            model.interconnects, gridStep, model.params,
                            model.paramValues, model.defaultParamsIndex)
    
    # get one block data for test
    block = generator.blocks[0]
    blockData = generator.getBlockInfo(block, 0)
    # print("blockData = ")
    # print(blockData)

    # get central funcion
    systemsForCentralFuncs, numsForSystems = blockData[0], blockData[1]
    cf, arrWithFunctionNames = generator.generateCentralFunctionCode(block, 0,
                                                                     systemsForCentralFuncs,
                                                                     numsForSystems)
    
    _sign = generator.generateFunctionSignature(0, 'test_signature',
                                                ['1', '2', '3'])
    print("signature = ")
    print(_sign)
    print("systemsForCentralFuncs = ")
    print(systemsForCentralFuncs)
    # print("numsForSystems = ")
    # print(numsForSystems)

    print("cf = ")
    print(cf)
    print("arrW = ")
    print(arrWithFunctionNames)
    return(generator)
    # return(systemsForCentralFuncs[0])


def test_block():
    '''
    DESCRIPTION:
    What is block.
    '''
    block = Block("test", 2)
    print(block.getCellCount(0.1, 0.1, 0.1))
    return(block.getPropertiesDict())
