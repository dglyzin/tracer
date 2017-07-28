from domainmodel.criminal.parser import Parser
from domainmodel.criminal.derivCodeGenerator import MixDerivGenerator
from domainmodel.criminal.cppOutsForTerms import CppOutsForTerms
import logging
import sys

# for independet launching this module
#logging.basicConfig(level=logging.DEBUG)

# create logger that child of tests.tester loger
logger = logging.getLogger('tests.tester.criminal.tests')


def test_powers():
    parser = Parser()
    parser = fill_params_for_diff(parser)
    
    eqs = ["U^3", "V(t-1.1,{x, 0.7})^3",
           "D[V(t-1.1),{x, 2}]^3"]
    for eq in eqs:
        logger.debug('########')
        logger.debug('for eq =')
        logger.debug(eq)
        try:
            parser.parseMathExpression(eq)
        except:
            raise(ParserException(testName='powers',
                                  eq=eq))
        logger.debug("out")
        logger.debug(parser.out)
    assert(True)


def simple_test_power(eq='U(t-1)^3'):
    parser = Parser()
    parser.parseMathExpression(eq)
    return(parser)


def test_diff_outs():
    '''
    DESCRIPTION:
    Tests get_out_for_termDiff for
    different parameters.
    '''
    tests = [['pure', 'common', ['x']],
             ['pure', 'special', ['x']],
             ['pure', 'interconnect', ['x']],
             ['pure', 'None', ['x']],
             ['mix', 'common', ['x', 'y']],
             ['mix', 'special', ['x', 'y']],
             ['mix', 'special', ['y', 'x']],
             ['mix', 'None', ['x', 'y']]]

    for test in tests:
        logger.debug("#######")
        logger.debug("mix, None")
        try:
            out = diff_out(*test)
        except:
            e = ParserException(testName='test_diff_outs',
                                testArgs='diff,'+str(test),
                                eq=None)
            logger.debug(e.data[1])
            raise(e)
        logger.debug(out)
    assert(True)


def diff_out(diffType, diffMethod, vars, deriveOrder=2,
             func="sin(arg_X, arg_Y)*arg_T"):
    parser = Parser()
    parser = fill_params_for_diff(parser)

    # main params
    parser.params.diffType = diffType
    parser.params.diffMethod = diffMethod
    parser.params.indepVarList = vars
    parser.params.derivOrder = deriveOrder
    # parser.params.leftOrRightBoundary = 0 or 1
    parser.params.unknownVarIndex = 0
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

    logger.debug('########')
    logger.debug('for method None ')
    parser.params.diffMethod = 'None'
    try:
        parser.parseMathExpression(eq)
    except:
        e = ParserException(testName='test_diff_parser',
                            testArgs='diff, parser, None',
                            eq=eq)
        logger.debug(e.data[1])
        raise(e)

    logger.debug("out")
    logger.debug(parser.out)

    logger.debug('########')
    logger.debug('for method common ')
    parser.params.diffMethod = 'common'
    try:
        parser.parseMathExpression(eq)
    except:
        e = ParserException(testName='test_diff_parser',
                            testArgs='diff, parser, common',
                            eq=eq)
        logger.debug(e.data[1])
        raise(e)

    logger.debug("out")
    logger.debug(parser.out)

    logger.debug('########')
    logger.debug('for method special ')
    parser.params.diffMethod = 'special'
    try:
        parser.parseMathExpression(eq)
    except:
        e = ParserException(testName='test_diff_parser',
                            testArgs='diff, parser, special',
                            eq=eq)
        logger.debug(e.data[1])
        raise(e)

    logger.debug("out")
    logger.debug(parser.out)

    try:
        logger.debug('########')
        logger.debug('for method interconnect ')
        parser.params.diffMethod = 'interconnect'
        parser.parseMathExpression(eq)
        logger.debug("out")
        logger.debug(parser.out)
    except:
        logger.debug("interconnect fail"
              + " prabobly for mix")
    assert(True)


def fill_params_for_diff(parser):
    '''
    DESCRIPTION:
    '''
    # PARAMS FOR ALL
    parser.params.blockNumber = 0

    # should detect
    parser.params.indepVarList = ['x']
    parser.params.derivOrder = 2

    parser.params.diffType = 'pure'
    parser.params.diffMethod = 'common'
    parser.params.parameters = ['a', 'b']
    parser.params.parametersVal = {'a': 1, 'b': 2}
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
    bounds_1d()
    bounds_2d()
    assert(True)


def bounds_1d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '1D'
    parser.params.shape = [100]
    parser.params.parameters = ['a']
    parser.params.parametersVal = {'a': 0.5}

    eqs = ["-(U(t,{x, a}))", "-(U(t,{x, 0.7}))",
           "-(V(t-1.1,{x, a}))", "-(V+U)"]
    for eq in eqs:
        logger.debug('for eq = ')
        logger.debug(eq)
        try:
            parser.parseMathExpression(eq)
        except:
            e = ParserException(testName='bound1d',
                                eq=eq)
            logger.debug(e.data[1])
            raise(e)
        logger.debug("out = ")
        logger.debug(parser.out)
        logger.debug('##############')

    return(parser)


def bounds_2d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '2D'
    parser.params.shape = [100, 1000]
    parser.params.parameters = []
    parser.params.parametersVal = {}

    eqs = ["-(W(t,{x, 0.7}{y, 0.3}))",
           "-(U(t-1.1,{x, 0.7}{y, 0.3}))"]
    for eq in eqs:
        logger.debug('for eq = ')
        logger.debug(eq)
        try:
            parser.parseMathExpression(eq)
        except:
            e = ParserException(testName='bound2d',
                                eq=eq)
            logger.debug(e.data[1])
            raise(e)
        logger.debug("out = ")
        logger.debug(parser.out)
        logger.debug('##############')
    return(parser)


class ParserException(Exception):
    '''
    DESCRIPTION:
    For cathing error of parser.
    For tests cases in tester.py.
    '''
    def __init__(self, testName, testArgs=None, eq=None):
        self.testName = testName
        self.testArgs = testArgs
        self.eq = eq
        self.data = sys.exc_info()
        logger.error(self.testName)
        logger.error(self.testArgs)
        logger.error(self.eq)
        logger.error(self.data[1])
        logger.error('line ' + str(self.data[2].tb_lineno))
