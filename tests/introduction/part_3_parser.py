'''
DESCRIPTION:
Some functions for understanding how
parser work.

From most general to particlular.

parseMathExpression method of MathExpressionParser
used for creating parsing list from equation string.
for example:
    eqStr ="U'=a*(D[U(t-1),{y,2}])"
    out = [u'a', '*', '(',
           ['D[', [u'U', '(', 't', '-', u'1', ')'],
           ',', '{', u'y', ',', u'2', '}', ']'], ')']
 
generateRightHandSideCodeDelay method of RHSCodeGenerator
used for translate parser list to .cpp function.
for example
    parserList = out (from example above)
    outCpp = '\t result[idx + 0] = params[0] * ('
             + '(DYM2 * (1 * source[1][idx + 1 * '
             + 'Block0StrideY * Block0CELLSIZE + 0'
             + '] - 2 * source[1][idx + 0 * '
             + 'Block0StrideY * Block0CELLSIZE + 0]'
             + '1 * source[1][idx-1 * Block0StrideY'
             + '* Block0CELLSIZE + 0])));\n'

createParsePattern method of ParsePatternCreater
used for creating a grammar ( in other words:
creating character sets with We search for
in equation string).
for example (more examples in pyparsing_examples folder)
   # define grammar of a greeting
   greet = Word(alphas) + "," + Word(alphas) + "!"

   hello = "Hello, World!"
   print (hello, "->", greet.parseString(hello))

   The program outputs the following:

   Hello, World! -> ['Hello', ',', 'World', '!']

REFERENCES:

pyparsing API doc:
https://pythonhosted.org/pyparsing/

pyparsing examples:
https://pythonhosted.org/pyparsing/
'''
from domainmodel.equationParser import MathExpressionParser
from domainmodel.rhsCodeGenerator import RHSCodeGenerator

from pyparsing import Literal, Word, nums, alphas, Group
from pyparsing import Forward, Optional, OneOrMore, Suppress
from pyparsing import restOfLine, ZeroOrMore
from domainmodel.equationParser import CorrectnessController, ParsePatternCreater
from tests.introduction.part_2_generators import get_gen2D_for_test
from tests.introduction.part_2_2_gen_bouns import BlockInfo


def test_generateBoundsAndIcs(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    Generator2D.generateBoundsAndIcs
    '''
    gen = get_gen2D_for_test(modelFile).generator
    gen.generateAllDefinitions()
    
    blockInfo = BlockInfo(gen.blocks[0])
    blockInfo.getBlockInfo(gen, 0)
    
    cf, arrWithFunctionNames = gen.generateCentralFunctionCode(gen.blocks[0], 0,
                                                               blockInfo.systemsForCentralFuncs,
                                                               blockInfo.numsForSystems)

    bf = gen.generateBoundsAndIcs(gen.blocks[0], 0,
                                  arrWithFunctionNames,
                                  blockInfo.blockFuncMap,
                                  blockInfo.totalBCondLst,
                                  blockInfo.totalInterconnectLst)
    return(bf)


def test_generate_vertex(modelFile="tests/short_restest_full.json"):

    gen = get_gen2D_for_test(modelFile).generator
    gen.generateAllDefinitions()
    
    blockInfo = BlockInfo(gen.blocks[0])
    blockInfo.getBlockInfo(gen, 0)
    
    cf, arrWithFunctionNames = gen.generateCentralFunctionCode(gen.blocks[0], 0,
                                                               blockInfo.systemsForCentralFuncs,
                                                               blockInfo.numsForSystems)
    
    parser = MathExpressionParser()
    gen.parseBoundaryConditions(blockInfo.totalBCondLst, parser)
    parsedVertexCondList = gen.createVertexCondLst(blockInfo.totalBCondLst)
    
    print("parsedVertexCondList =")
    print(parsedVertexCondList)
    vertexFunctions = gen.generateVertexFunctions(0,
                                                  arrWithFunctionNames,
                                                  parsedVertexCondList)
    return(vertexFunctions)


def get_parse_pattern(eqStr=u"U'=a*(D[U(t-1),{x,2}] + D[U(t-9.2),{y,2}])"):
    '''
    DESCRIPTION:
    What is parser (MathExpressionParser)
    and what it do.
    
    INPUT:
    Equation string with only single params:
       a
    and independent vars:
       x, y.
    '''
    eqSys = [eqStr]
    # eqStr = eqSys[0]
    print("eq = ")
    print(eqSys[0])

    parser = MathExpressionParser()

    # vars like U
    vars = parser.getVariableList(eqSys)
    print("vars = ")
    print(vars)
        
    # some errors checking
    controller = CorrectnessController()
    controller.emptyControl(eqStr)
    controller.controlOperators(eqStr)
    controller.controlBrackets(eqStr)

    # load patterns
    ppc = ParsePatternCreater()
    return(ppc)


def test_parser_cpp(eqStr=u"U'=a*(D[U(t-1),{y,2}])"):
    '''
    DESCRIPTION:
    Generate cpp code from equation
    for central function.
    (i.e. how RHSCodeGenerator work)
    '''

    parser = MathExpressionParser()

    # eqSys = [u"U'=a*(D[U,{x,2}] + D[U(t-1),{y,2}])+U(t-1)"]
    eqSys = [eqStr]
    print("eq = ")
    print(eqSys[0])

    # vars like U
    vars = parser.getVariableList(eqSys)
    print("vars = ")
    print(vars)

    # independent variables
    userIndepVars = [u'x', u'y']
    params = [u'a']
    
    equationStr = eqSys[0]

    # delays used for storing k 
    # where k: U(t-k) exist in 
    #          equation string
    delays = []

    # equation string to parsing list
    equationRightHandSide = parser.parseMathExpression(equationStr, vars,
                                                       params, userIndepVars,
                                                       delays)
    print("right = ")
    print(equationRightHandSide)
    
    # parsing list to cpp
    b = RHSCodeGenerator()
    out = b.generateRightHandSideCodeDelay(0, vars[0], equationRightHandSide,
                                           userIndepVars, vars, params,
                                           delay_lst=delays)
    return(out)


def test_pypars():
    pass
    '''
    variable = Literal("U")
    variable = Group(variable+"("+"t"+"-"+real+")") ^ variable
    for var in variableList:
        variable = variable^Literal(var)

    order = '{' + indepVariable + ',' + integer + '}'
    derivative = 'D['+ variable + ','+ order + ZeroOrMore(',' + order) + ']'

    funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')
    unaryOperation = Literal('-')^funcSignature
    binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')
    if countOfParams > 0:
        operand = variable^parameter^Group(derivative)^real^indepVariable
    else:
        operand = variable^Group(derivative)^real^indepVariable
    '''


def test_parser_eq(eqStr=u"U'=a*(D[U(t-1),{x,2}] + D[U(t-9.2),{y,2}])"):
    '''
    DESCRIPTION:
    What is parser (MathExpressionParser)
    and what it do.
    '''
    ppc = get_parse_pattern(eqStr)

    # return(parsePatternDelays.parseString(eqStr))
    delays = []

    # independent variables
    userIndepVars = [u'x', u'y']
    params = [u'a']
    parsePattern = ppc.createParsePattern(vars, params, userIndepVars, delays)


    print("parsePattern = ")
    print(parsePattern)

    # parse equation string
    parsedExpression = parsePattern.parseString(eqStr).asList()
    
    print("parsedExpression = ")
    print(parsedExpression)
    return(delays)
    # postprocessing
    controller.controlPowers(parsedExpression)
    # parser.__concatPower(parsedExpression)
    controller.controlDerivatives(parsedExpression, userIndepVars)  # args[-1]
    
    return parsePattern
