from pyparsing import Literal, Word, nums, alphas
from pyparsing import Group, Forward, Optional
from pyparsing import Suppress, restOfLine
from pyparsing import OneOrMore, ZeroOrMore


class Parser():
    def __init__(self):
        '''
        TODO:
        self.real.copy()
        '''
        self.outForTermVarsPoint = 'source[arg1][arg3*Darg2M1*CELLSIZE]'

        self.delays = []
        self.dataTermVarsPoint = []

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
 
        # terms
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
        action1 = lambda *args: self.action_generate_out_for_termVarsPoint(*args)
        self.termVarsPoint = Group(self.termVarsSimple
                                   + "("
                                   + self.termArgs.setParseAction(action)
                                   + "-" + self.real.setParseAction(action_spec) + ','
                                   + OneOrMore(Group("{"
                                                     + self.termArgs.setParseAction(action) + ','
                                                     + self.real.copy().setParseAction(action) + '}'))
                                   + ")").setParseAction(action1)

        self.termVars = self.termVarsPoint ^ self.termVarsDelay ^ self.termVarsSimple
        
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
        try:
            parsedExpression = self.eqExpr.parseString(expr)
        except:
            print("expr is not a equation")
            parsedExpression = self.baseExpr.parseString(expr)
        return(parsedExpression)

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
    
    def action_generate_out_for_termVarsPoint(self, *args):  # str, loc, toks
        self.out = self.outForTermVarsPoint
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
