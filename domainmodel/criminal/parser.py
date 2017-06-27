'''
DESCRIPTION:
For undirect changes in original scheme.

'''
from pyparsing import Literal, Word, nums, alphas
from pyparsing import Group, Forward, Optional
from pyparsing import Suppress, restOfLine
from pyparsing import OneOrMore, ZeroOrMore
from domainmodel.criminal.params import Params
from domainmodel.criminal.cppOutsForTerms import CppOutsForTerms


class Parser():
    '''
    DESCRIPTION:
    Use one general pattern for all parsing.
    This pattern composed from local patterns,
    each of which can be replaced by .cpp string
    by actions. That .cpp strings can contain argi
    elements for replacing it by founded values (like
    var names, value ...) (see action_add_args).
    In that case arg1 means first added args by some
    local pattern, arg2 -second ...

    FOR EXAMPLE:
    if pattern looks like:
    Group(locPatt1.setParseAction(action_add_args)
          + locPatt2.setParseAction(action_add_args))
    and
    outForTerm looks like 'source[arg1][arg2]'
    then
    arg1 will be arg, corresponded to locPatt1
    arg2 will be arg, corresponded to locPatt2

    TODO:
    Can load .cpp paterns form .json config file
    (like outForTerm.. ).
    Can load terms and actions from extern files.
    '''
    def __init__(self, blockNumber=None, dim='1D'):
        '''
        TODO:
        self.real.copy()
        '''
        # parameters fill
        self.params = Params()
        self.params.dim = dim
        if blockNumber is not None:
            self.blockNumber = blockNumber
            self.params.blockNumber = blockNumber
        else:
            self.blockNumber = 0
            self.params.blockNumber = 0
        self.dim = dim

        # cpp outs
        self.cppOut = CppOutsForTerms(self.params)

        # data for actions arg's (in outFor.. string)
        self.delays = []
        self.dataTermVarsPoint = []

        # base elements
        self.vars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.args = 'xyzt'
        self.params = self.vars.lower()
        for a in self.args:
            self.params.replace(a, "")
        self.func = ['exp', 'sqrt', 'log',
                     'sin', 'cos', 'tan',
                     'sinh', 'tanh']
        self.unary = ['-']
        self.binary = ['+', '-', '*', '/', '^']
 
        # terms (!replace in different file)
        self.integer = Word(nums)
        self.real = Word(nums + '.')
        self.termParam = reduce(lambda x, y: Literal(y) ^ x,
                                self.params,
                                Literal(self.params[0]))
        self.termArgs = reduce(lambda x, y: Literal(y) ^ x,
                               self.args,
                               Literal(self.args[0]))
        self.termFunc = reduce(lambda x, y: Literal(y) ^ x,
                               self.func,
                               Literal(self.func[0]))
        self.termUnary = reduce(lambda x, y: Literal(y) ^ x,
                                self.unary,
                                Literal(self.unary[0]))
        self.termBinary = reduce(lambda x, y: Literal(y) ^ x,
                                 self.binary,
                                 Literal(self.binary[0]))
        # self.termOperand = real ^ indepVariable ^ parameter
        self.termVarsSimple = reduce(lambda x, y: Literal(y) ^ x,
                                     self.vars,
                                     Literal(self.vars[0]))

        action = lambda str, loc, toks: self.action_add_delay(str, loc, toks)
        self.termVarsDelay = Group(self.termVarsSimple
                                   + "("
                                   + self.termArgs+"-"+self.real
                                   + ")").setParseAction(action)

        action = lambda str, loc, toks: self.action_add_args(self.dataTermVarsPoint,
                                                             str, loc, toks)
        action_spec = lambda str, loc, toks: self.action_add_args_spec(self.dataTermVarsPoint,
                                                                       str, loc, toks)
        action1 = lambda *args: self.action_generate_out('termVarsPointDelay', *args)
        self.termVarsPointDelay = Group(self.termVarsSimple
                                        + "("
                                        + self.termArgs.setParseAction(action)
                                        + "-" + self.real.setParseAction(action_spec) + ','
                                        + OneOrMore(Group("{"
                                                          + self.termArgs.setParseAction(action) + ','
                                                          + self.real.copy().setParseAction(action) + '}'))
                                        + ")").setParseAction(action1)
        action2 = lambda *args: self.action_generate_out('termVarsPoint', *args)
        self.termVarsPoint = Group(self.termVarsSimple
                                   + "("
                                   + self.termArgs.setParseAction(action)
                                   + ','
                                   + OneOrMore(Group("{"
                                                     + self.termArgs.setParseAction(action) + ','
                                                     + self.real.copy().setParseAction(action) + '}'))
                                   + ")").setParseAction(action2)

        self.termVars = (self.termVarsPoint ^ self.termVarsPointDelay
                         ^ self.termVarsDelay ^ self.termVarsSimple)
        
        self.termOrder = '{' + self.termArgs + ',' + self.integer + '}'
        self.termDiff = ('D[' + self.termVars + ','
                         + self.termOrder + ZeroOrMore(',' + self.termOrder)
                         + ']')

        self.termOperand = (self.termVars ^ self.termParam ^ Group(self.termDiff)
                            ^ self.real ^ self.termArgs ^ self.termParam)

        self.recUnary = Forward()
        self.recUnary << ((Literal('(') ^ self.termUnary)
                          + Optional(self.recUnary))

        self.baseExpr = Forward()
        self.baseExpr << (Optional(self.recUnary) + self.termOperand
                          + Optional(OneOrMore(')'))
                          + Optional(self.termBinary)
                          + Optional(self.baseExpr))

        # self.rhsExpr = Forward()
        # self.rhsExpr << (self.baseExpr
        #                  + Optional(OneOrMore(')'))
        #                  + Optional(self.termBinary)
        #                  + Optional(self.rhsExpr))

        self.eqExpr = (Suppress(self.termVarsSimple + "'" + '=')
                       + self.baseExpr)  # self.rhsExpr

    def parseMathExpression(self, expr):
        self.clear_data()
        try:
            parsedExpression = self.eqExpr.parseString(expr)
        except:
            print("expr is not a equation")
            parsedExpression = self.baseExpr.parseString(expr)
        return(parsedExpression)

    def clear_data(self):
        '''
        DESCRIPTION:
        Clear terms data for reusing.
        '''
        self.dataTermVarsPoint = []

    def action_add_delay(self, str, loc, toks):
        '''
        DESCRIPTION:
        If delay U(t-k) found, add k to delays
        where delays is global.
        Cannot work with system with vars U,V,...
        where more then one var has delays.
        '''
        # print("toks=")
        # print(toks)
        delay = float(toks.asList()[0][4])
        self.delays.append(delay)

    def action_add_args(self, termData, str, loc, toks):
        '''
        DESCRIPTION:
        Place all found args in termData
        in occurrance order.
                        
        '''
        # print("toks = ")
        # print(toks)
        if toks[0] in "xyz":
            data = toks[0].upper()
        else:
            data = toks[0]
        termData.append(data)
    
    def action_add_args_spec(self, termData, str, loc, toks):
        '''
        DESCRIPTION:
        Place all found args in termData
        in occurrance order.
        Spec for delays.
                        
        '''
        print("toks = ")
        print(toks)
        data = toks[0].split('.')[0]
        termData.append(data)
    
    def action_generate_out(self, termName, *args):
        '''
        DESCRIPTION:
        Add founded by paterns with termName
        arg's (like argi) to out string.
        Use out from cppOutsForTerms
        (so it should be here)
        '''
        self.out = self.cppOut.get_out_for_term(termName)
        print("dataTermVarsPoint =")
        print(self.dataTermVarsPoint)
        for i in range(len(self.dataTermVarsPoint)):
            self.out = self.out.replace("arg%d" % i,
                                        self.dataTermVarsPoint[i])

    def action_generate_out_for_termVarsPoint(self, *args):
        '''
        DESCRIPTION:
        Add founded by paterns termVarsPoint
        arg's (like argi) to out string.
        '''
        if self.dim == '1D':
            self.out = self.outForTermVarsPoint1D
        elif self.dim == '2D':
            self.out = self.outForTermVarsPoint2D

        print("dataTermVarsPoint =")
        print(self.dataTermVarsPoint)
        for i in range(len(self.dataTermVarsPoint)):
            self.out = self.out.replace("arg%d" % i,
                                        self.dataTermVarsPoint[i])

    def test(self):
        eqStrList = [u"U'=D[U(t-1.1),{y,1}]+D[U(t-5.9),{y,2}]+U(t-1)",
                     u"U'=a*(D[U,{y,2}])+U(t-3)",
                     u"U'=a*(D[U(t-2),{y,3}])+U(t-3)",
                     u"U'=a*(D[U(t-1),{y,2}] + D[U(t-5),{x,1}])"]
        for eq in eqStrList:
            print("eq = %s" % eq)
            print(self.parseMathExpression(eq))
