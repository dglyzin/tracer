from pyparsing import Literal, Word, nums, alphas, Group, Forward, Optional, OneOrMore, Suppress, restOfLine

class Parser:
# created to control count of boundaries in equation.
    def __boundaryController(self,estr):
        count = 0
        for char in estr:
            if char == '(':
                count = count + 1
            elif char == ')':
                count = count - 1
        return count

# created to control correctness of location of binary operators in equation
    def __correctOperationSequence(self,estr):
        correct = True
        operationList = list(['+','-','*','/','^'])
        length = len(estr)
        for i,char in enumerate(estr):
            if char in operationList and ( (i > 1 and estr[i-1] in operationList) or (i < length - 2 and estr[i+1] in operationList)):
                correct = False
                break
        return correct

# build string '^3' from sequence of array elements of the type '^','3'
    def __concatPower(self,lst):
        index = 0
        while lst.count('^') > 0:
            index = lst.index('^',index)
            power = lst[index + 1]
            lst.pop(index)
            lst.pop(index)
            power = '^' + power
            lst.insert(index,power)

    def getRhsLst(self,estrList,parList):
        real = Word(nums + '.')
        integer = Word(nums)
        
        parameter = Literal(parList[0])
        for par in parList:
            parameter = parameter^Literal(par)
            
        varLst = self.getLhsList(estrList)
        variable = Literal(varLst[0])
        for var in varLst:
            variable = variable^Literal(var)
            
        indepVariable = Word(alphas + nums)
        derivative = 'D['+ variable + ','+ '{' + indepVariable + ',' + integer + '}' + ']'
    
        funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')
        unaryOperation = Literal('-')^funcSignature
        binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')
        operand = variable^parameter^Group(derivative)^real
    
        recursiveUnaryOperation = Forward()
        recursiveUnaryOperation << (Literal('(')^unaryOperation) + Optional(recursiveUnaryOperation)
        base_expr = Forward()
        base_expr << Optional(recursiveUnaryOperation) + operand + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(base_expr)
        rhs_expr = Forward()
        rhs_expr << base_expr + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(rhs_expr)
    
    # Pattern for equation parsing
        equation_expression = Suppress(variable + "'" + '=') + rhs_expr
    
        rhsLst = list([])
        for eq in estrList:
            if not self.__correctOperationSequence(eq):
                raise SyntaxError('Some binary operators are located uncorrectly in the equation ' + eq + ' !')            
            boundaryCount = self.__boundaryController(eq)
            if boundaryCount < 0:
                raise SyntaxError('Either too more closing brackets or there is a lack of opening brackets in equation ' + eq + ' !')            
            elif boundaryCount > 0:
                raise SyntaxError('Either too more opening brackets or there is a lack of closing  brackets in equation ' + eq + ' !')            
            rhsLst.extend([equation_expression.parseString(eq).asList()])
    
    # It is comfortable to store expressions such ^3 as a string
        for parsedEq in rhsLst:
            self.__concatPower(parsedEq)
        return rhsLst

    def getLhsList(self,estrList):
        variable = Word(alphas + nums)
        lhs_expression = variable + Suppress(restOfLine)
        out = list([])
        for eq in estrList:
            out.extend(lhs_expression.parseString(eq).asList())
        return out