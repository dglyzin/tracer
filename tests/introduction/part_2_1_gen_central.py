'''
DESCRIPTION:
Tests for central functions.
'''

from part_2_generators import Equation, get_model_for_tests
from part_2_generators import AbstractGenerator, Generator2D


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

