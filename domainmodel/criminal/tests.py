from domainmodel.criminal.parser import Parser
from domainmodel.criminal.derivCodeGenerator import MixDerivGenerator


def test_diff_mix(eq="D[U(t-1.1),{x,2}]+D[U(t-5.1),{y,2}]+D[V(t-1.1),{x,1}]"):
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '1D'
    parser.params.shape = [100]
    
    parser.params.unknownVarIndex = 'uvi'
    parser.params.indepVarList = ['x', 'y']
    parser.params.indepVarIndexList = [' $ indepVarIndexList $ ']

    parser.params.derivOrder = 2
    parser.params.userIndepVariables = ['x', 'y']
    parser.params.parsedMathFunction = 'sin(x)'
    parser.params.side = 0
    parser.params.firstIndex = -1  # >=0
    parser.params.secondIndexSTR = " $ secondIndexSTR $ "

    # for delays:
    parser.params.delay = str(" $ delay $ ")

    pdg = MixDerivGenerator(parser.params)
    return(pdg)


def test_diff_pure(eq="D[U(t-1.1),{x,2}]+D[U(t-5.1),{y,2}]+D[V(t-1.1),{x,1}]"):
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

    # pdg = PureDerivGenerator(parser.params)

    print('########')
    print('for method common ')
    parser.params.diffMethod = 'None'
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

    print('########')
    print('for method common ')
    parser.params.diffMethod = 'common'
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

    print('########')
    print('for method special ')
    parser.params.diffMethod = 'special'
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

    print('########')
    print('for method interconnect ')
    parser.params.diffMethod = 'interconnect'
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

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
