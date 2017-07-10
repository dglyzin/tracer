from domainmodel.criminal.parser import Parser
from domainmodel.criminal.derivCodeGenerator import MixDerivGenerator
from domainmodel.criminal.cppOutsForTerms import CppOutsForTerms


def test_powers():
    parser = Parser()
    parser = fill_params_for_diff(parser)
    
    print('########')
    eq = "U^3"
    print('for eq =')
    print(eq)
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

    print('########')
    eq = "V(t-1.1,{x, 0.7})^3"
    print('for eq =')
    print(eq)
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)

    print('########')
    eq = "D[V(t-1.1),{x, 2}]^3"
    print('for eq =')
    print(eq)
    parser.parseMathExpression(eq)
    print("out")
    print(parser.out)


def test_power(eq='U(t-1)^3'):
    parser = Parser()
    parser.parseMathExpression(eq)
    return(parser)


def test_diff():
    '''
    DESCRIPTION:
    Tests get_out_for_termDiff for
    different parameters.
    '''
    # for pure
    print("pure, common")
    out = test_diff_out('pure', 'common', ['x'])
    print(out)

    print("#######")
    print("pure, special")
    out = test_diff_out('pure', 'special', ['x'])
    print(out)

    print("#######")
    print("pure, interconnect")
    out = test_diff_out('pure', 'interconnect', ['x'])
    print(out)

    print("#######")
    print("pure, None")
    out = test_diff_out('pure', 'None', ['x'])
    print(out)

    # for mix
    print("#######")
    print("mix, common")
    out = test_diff_out('mix', 'common', ['x', 'y'])
    print(out)

    print("#######")
    print("mix, special, dxdy")
    out = test_diff_out('mix', 'special', ['x', 'y'])
    print(out)

    print("#######")
    print("mix, special, dydx")
    out = test_diff_out('mix', 'special', ['y', 'x'])
    print(out)

    print("#######")
    print("mix, None")
    out = test_diff_out('mix', 'None', ['x', 'y'])
    print(out)


def test_diff_out(diffType, diffMethod, vars, deriveOrder=2,
                  func="sin(arg_X, arg_Y)*arg_T"):
    parser = Parser()
    parser = fill_params_for_diff(parser)

    # main params
    parser.params.diffType = diffType
    parser.params.diffMethod = diffMethod
    parser.params.indepVarList = vars
    parser.params.derivOrder = deriveOrder
    # parser.params.leftOrRightBoundary = 0 or 1
    
    cppOut = CppOutsForTerms(parser.params)

    # func
    cppOut.dataTermMathFuncForDiffSpec = func
    pdg = cppOut.get_out_for_termDiff()
    return(pdg)


def test_diff_parser(eq=("D[U(t-1.1),{x,2}]+D[U(t-5.1),{y,2}]"
                         + "+D[V(t-1.1),{x,1}]"),
                     func="sin(arg_X, arg_Y)*arg_T"):
    '''
    DESCRIPTION:
    Test parser for different parameters.

    ! D[U,{x,2}] can themself detect diff argument
    (i.e. x) if indepVarList =['x']

    TODO:
    TermDiff must themself detect args.
    '''
    parser = Parser()
    parser = fill_params_for_diff(parser)
    
    # for special
    parser.cppOut.dataTermMathFuncForDiffSpec = func

    print('########')
    print('for method None ')
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

    try:
        print('########')
        print('for method interconnect ')
        parser.params.diffMethod = 'interconnect'
        parser.parseMathExpression(eq)
        print("out")
        print(parser.out)
    except:
        print("interconnect fail"
              + " prabobly for mix")
    return(parser)


def fill_params_for_diff(parser):
    # PARAMS FOR ALL
    parser.params.blockNumber = 0
    parser.params.unknownVarIndex = ' $ unknownVarIndex[0] $ '
    parser.params.indepVarList = ['x']
    parser.params.derivOrder = 2
    parser.params.diffType = 'pure'
    parser.params.diffMethod = 'common'
    # END FOR ALL
    
    # PARAMS FOR BOUND
    parser.params.dim = '1D'
    parser.params.shape = [100]
    # END FOR BOUND
    
    # PARAMS FOR SPECIAL
    # for special_diff of pure:
    # parser.params.leftOrRightBoundary = 0  # or 1
    parser.params.side = 0
    # END FOR SPECIAL

    # PARAMS FOR INTERCONNECT
    parser.params.firstIndex = -1  # >=0
    parser.params.secondIndexSTR = " $ secondIndexSTR $ "
    # END FOR INTERCONNECT
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
