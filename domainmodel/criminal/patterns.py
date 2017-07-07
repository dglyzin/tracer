from pyparsing import Literal, Word, nums, alphas
from pyparsing import Group, Forward, Optional
from pyparsing import Suppress, restOfLine
from pyparsing import OneOrMore, ZeroOrMore


class Patterns():
    def __init__(self):
        self.load_atoms_for_patterns()
        self.load_base_patterns()
        self.load_all_patterns()

    def load_all_patterns(self):

        # self.termOperand = real ^ indepVariable ^ parameter
        self.termVarsSimple = reduce(lambda x, y: Literal(y) ^ x,
                                     self.vars,
                                     Literal(self.vars[0]))

        self.termVarsSimpleIndep = self.termVarsSimple.copy()
 
        # TERM FOR U(t-1.9)
        # self.termVarsForDelay = self.termVarsSimple.copy()
        self.termVarsDelay = Group(self.termVarsSimpleIndep
                                   + "("
                                   + self.termArgs+"-"+self.real
                                   + ")")  # .setParseAction(action)
        # END OF TERM

        # TERM FOR  U(t-1.3,{x,0.3}{y,0.7})
        # OR U(t-1.3,{x,0.3})
        # for args for termVarsPointDelay
        self.termArgForVarDelayT = self.termArgs.copy()
        self.termRealForVarDelayT = self.real.copy()
        self.termArgForVarDelayX = self.termArgs.copy()
        self.termRealForVarDelayX = self.real.copy()
        
        # term for U(t-1.3,{x,0.3}{y,0.7}) or
        # for U(t-1.3,{x,0.3})
        
        self.termVarsPointDelay = Group(self.termVarsSimple
                                        + "("
                                        + (self.termArgForVarDelayT
                                           + Optional(ZeroOrMore("-"))
                                           + ZeroOrMore(self.termRealForVarDelayT))
                                        + ','
                                        + OneOrMore(Group("{"
                                                          + self.termArgForVarDelayX + ','
                                                          + self.termRealForVarDelayX + '}'))
                                        + ")")
        # END OF TERM

        self.termVars = (self.termVarsPointDelay
                         ^ self.termVarsDelay ^ self.termVarsSimpleIndep)
        
        self.termOrder = '{' + self.termArgs + ',' + self.integer + '}'
        self.termDiff = ('D[' + self.termVars + ','
                         + self.termOrder + ZeroOrMore(',' + self.termOrder)
                         + ']')

        self.termOperand = (self.termVars ^ self.termParam ^ Group(self.termDiff)
                            ^ self.real ^ self.termArgs ^ self.termParam)
        
        # FOR TERM like -(-sin(x)+cos(x))*U
        self.termBrackets = Literal('(') ^ Literal(')')
        self.termRealForUnary = self.real.copy()
        self.termArgsForUnary = self.termArgs.copy()
        self.termFuncArg = Group(self.termFunc
                                 + self.termBrackets
                                 + self.termArgsForUnary
                                 + self.termBrackets)
        self.termUnaryFunc = (Group(ZeroOrMore(self.termUnary)
                                    + self.termRealForUnary)
                              ^ Group(self.termBrackets
                                      + OneOrMore(self.termUnary)
                                      + self.termRealForUnary
                                      + self.termBrackets)
                              ^ Group(ZeroOrMore(self.termUnary)
                                      + self.termFuncArg)
                              ^ Group(self.termBrackets
                                      + OneOrMore(self.termUnary)
                                      + self.termFuncArg
                                      + self.termBrackets))

        self.recUnary = Forward()

        self.recUnary << (Optional(self.termBrackets)
                          + self.termUnaryFunc
                          + Optional(self.termBinary)
                          + Optional(self.recUnary)
                          )
        # END OF TERM

        '''
        self.recUnary << ((Literal('(') ^ self.termUnary)
                          + Optional(self.recUnary))
        '''
        self.termBaseExpr = Forward()
        
        self.termBaseExpr << (Optional(self.termBrackets)
                              + Optional(self.termUnary)
                              + Optional(self.termBrackets)
                              + Optional(self.recUnary)
                              + Optional(self.termBrackets)
                              + Optional(self.termBinary)
                              + self.termOperand
                              + Optional(self.termBinary)
                              + Optional(self.termBaseExpr)
                          )
        '''
        self.baseExpr << (Optional(self.recUnary) + self.termOperand
                          + Optional(OneOrMore(')'))
                          + Optional(self.termBinary)
                          + Optional(self.baseExpr))
        '''
        self.eqExpr = (Suppress(self.termVarsSimple + "'" + '=')
                       + self.termBaseExpr)  # self.rhsExpr

    def load_base_patterns(self):
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

    def load_atoms_for_patterns(self):
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
 
