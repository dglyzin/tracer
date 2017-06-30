from domainmodel.criminal.parser import Parser
from domainmodel.criminal.derivCodeGenerator import PureDerivGenerator


def test_diff():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '1D'
    parser.params.shape = [100]
    
    parser.params.unknownVarIndex = ' $ unknownVarIndex[0] $ '
    parser.params.indepVarList = [' $ indepVarList[0] $ ']
    parser.params.indepVarIndexList = [' $ indepVarIndexList $ ']

    parser.params.derivOrder = 1
    parser.params.userIndepVariables = ['x', 'y']
    parser.params.parsedMathFunction = 'parsedMathFunction'
    parser.params.side = 0
    parser.params.firstIndex = -1  # >=0
    parser.params.secondIndexSTR = " $ secondIndexSTR $ "

    # for delays:
    parser.params.delay = str(" $ delay $ ")

    parser.params.diffMethod = 'None'
    pdg = PureDerivGenerator(parser.params)
    parser.parseMathExpression("D[U,{x,2}]")
    return(parser)


def test_bounds():
    parser1d = test_bounds_1d()
    parser2d = test_bounds_2d()

    return(parser1d)


def test_bounds_1d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '1D'
    parser.params.shape = [100]

    print('for eq = ')
    eq = "-(U(t,{x, 0.7}))"
    print(eq)
    parser.parseMathExpression(eq)
    print("out = ")
    print(parser.out)
    print('##############')

    print('for eq = ')
    eq = "-(V(t-1.1,{x, 0.7}))"
    print(eq)
    parser.parseMathExpression(eq)
    print("out = ")
    print(parser.out)
    print('##############')

    print('for eq = ')
    eq = "-(V+U)"
    print(eq)
    parser.parseMathExpression(eq)

    print("out = ")
    print(parser.out)
    print('##############')

    return(parser)


def test_bounds_2d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '2D'
    parser.params.shape = [100, 1000]

    print('for eq = ')
    eq = "-(W(t,{x, 0.7}{y, 0.3}))"
    print(eq)
    parser.parseMathExpression(eq)

    print("out = ")
    print(parser.out)
    print('##############')

    print('for eq = ')
    eq = "-(U(t-1.1,{x, 0.7}{y, 0.3}))"
    print(eq)
    parser.parseMathExpression(eq)

    print("out = ")
    print(parser.out)
    return(parser)
