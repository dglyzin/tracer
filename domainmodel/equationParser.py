# -*- coding: utf-8 -*-
from pyparsing import Literal, Word, nums, alphas, Group, Forward, Optional, OneOrMore, Suppress, restOfLine, ZeroOrMore

class CorrectnessController:
#     Со степенями не все проверено, например выражение "V'= a^2d + D[W,{z,2}]" распарсится до ['a','^','2'] и все функции создадутся!
    def emptyControl(self, stringForControl):
#         Проверяет, не пуста ли строка; если в строке уравнение, то не стоит ли после или до знака = пустота.
        if len(stringForControl) == 0:
            raise SyntaxError("Some equation or boundary condition was defined by empty string!")
        if stringForControl.startswith('=') or stringForControl.startswith("'"):
            raise SyntaxError("An equation " + stringForControl + " doesn't contain any left hand side!")
        if stringForControl.endswith('=') or stringForControl.endswith("'"):
            raise SyntaxError("An equation " + stringForControl + " doesn't contain any right hand side!")
    
    def controlBrackets(self, stringForControl):
        boundaryCount = 0
        for char in stringForControl:
            if char == '(':
                boundaryCount = boundaryCount + 1
            elif char == ')':
                boundaryCount = boundaryCount - 1
        if boundaryCount < 0:
            raise SyntaxError('Either too more closing brackets or there is a lack of opening brackets in the expression ' + stringForControl + '!')            
        elif boundaryCount > 0:
            raise SyntaxError('Either too more opening brackets or there is a lack of closing  brackets in the expression ' + stringForControl + '!')
    
    def controlOperators(self, stringForControl):
        operationList = list(['-','+','*','/','^'])
        length = len(stringForControl)
        for i,char in enumerate(stringForControl):
            leftIsOperator = i >= 1 and stringForControl[i-1] in operationList
            rightIsOperator = i <= length - 2 and stringForControl[i+1] in operationList
            rightIsBound = i <= length - 2 and stringForControl[i+1] == ')'
            isLast = i == length - 1
            firstAlternative = char in operationList and ( rightIsOperator or leftIsOperator or rightIsBound or isLast)
            secondAlternative = char in operationList[1:] and (i >= 1 and stringForControl[i-1] == '(' or i == 0)
            if firstAlternative or secondAlternative:
                raise SyntaxError('Some binary operators are located uncorrectly in expression ' + stringForControl + '!')

    def controlPowers(self, parsedStringForControl):
        for i,element in enumerate(parsedStringForControl):
            if element == '^':
                power = ''
                if i < len(parsedStringForControl) - 1:
                    power = parsedStringForControl[i + 1]
                #if not power.isdigit():
                #    raise SyntaxError('A power is absent or not an integer in some inputed function or equation!')
    
    def controlDerivatives(self, parsedStringForControl, independentVariableList):
        for expressionList in parsedStringForControl:
            if expressionList[0] == 'D[':
                for i,symbol in enumerate(expressionList):
                    if symbol == '{':
                        if expressionList[i+1] not in independentVariableList:
                            raise SyntaxError("Error in inputing of some derivative: independent variable, in which partial derivative should be calculated, is absent in list of independent variables!")
                        elif int(expressionList[i+3]) == 0:
                            raise SyntaxError("Error in inputing of some derivative: derivative should have positive order!")

class ParsePatternCreater:
    
    def parserPreprocForDelays(self, variableList, indepVariableList):
        real = Word(nums + '.')
        integer = Word(nums)
        
        indepVariable = Literal('t')
        for var in indepVariableList:
            indepVariable = indepVariable ^ Literal(var)
        
        variable = Literal(variableList[0])
        variable = Group(variable+"("+indepVariable+"-"+real+")")
        # rhs_expr = Forward()
        # rhs_expr << OneOrMore(variable) + ZeroOrMore(rhs_expr)
        return(variable)

    def __createParsePatternForDiffEquation(self, variableList,
                                            parameterList, indepVariableList,
                                            delays=[]):
        real = Word(nums + '.')
        integer = Word(nums)
        
        countOfParams = len(parameterList)
        if countOfParams > 0:
            parameter = Literal(parameterList[0])
            for par in parameterList:
                parameter = parameter ^ Literal(par)
            
        indepVariable = Literal('t')
        for var in indepVariableList:
            indepVariable = indepVariable ^ Literal(var)
        
        variable = Literal(variableList[0])
        
        def action_add_delay(str, loc, toks):
            '''
            DESCRIPTION:
            If delay U(t-k) found, add k to delays
            where delays is global.
            '''
            delay = float(toks.asList()[0][4])
            delays.append(delay)

        varDelay = Group(variable
                         + "("
                         + indepVariable+"-"+real
                         + ")").setParseAction(action_add_delay)
        
        variable = varDelay ^ variable
        for var in variableList:
            variable = variable ^ Literal(var)
        
        order = '{' + indepVariable + ',' + integer + '}'
        derivative = 'D['+ variable + ','+ order + ZeroOrMore(',' + order) + ']'
    
        funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')

        unaryOperation = Literal('-')^funcSignature
        binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')

        if countOfParams > 0:
            operand = variable^parameter^Group(derivative)^real^indepVariable
        else:
            operand = variable^Group(derivative)^real^indepVariable
        # print("operand = ")
        # print(operand)

        recursiveUnaryOperation = Forward()
        recursiveUnaryOperation << (Literal('(')^unaryOperation) + Optional(recursiveUnaryOperation)
        # print("recUnary = ")
        # print(recursiveUnaryOperation)

        base_expr = Forward()
        base_expr << Optional(recursiveUnaryOperation) + operand + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(base_expr)
        #print("base_expr = ")
        # print(base_expr)

        rhs_expr = Forward()
        rhs_expr << base_expr + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(rhs_expr)
    
        # Pattern for equation parsing
        return Suppress(variable + "'" + '=') + rhs_expr
        
    def __createParsePatternForMathFunction(self, parameterList, independentVariableList):
        '''
        DESCRIPTION:
        For parsing string like:
        'sin((x+3*a))'
            where a in parameterList
                  x in indepVariableList
        '''
        
        real = Word(nums + '.')
        
        countOfParams = len(parameterList)
        if countOfParams > 0:
            parameter = Literal(parameterList[0])
            for par in parameterList:
                parameter = parameter^Literal(par)
        
        if len(independentVariableList) == 0:
            raise AttributeError("Count of independent variables should be greater than 0!")
        indepVariable = Literal(independentVariableList[0])
        for var in independentVariableList:
            indepVariable = indepVariable^Literal(var)
    
        funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')
        unaryOperation = Literal('-')^funcSignature
        binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')
        if countOfParams > 0:
            operand = real^indepVariable^parameter
        else:
            operand = real^indepVariable
    
        recursiveUnaryOperation = Forward()
        recursiveUnaryOperation << (Literal('(')^unaryOperation) + Optional(recursiveUnaryOperation)
        base_expr = Forward()
        base_expr << Optional(recursiveUnaryOperation) + operand + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(base_expr)
        rhs_expr = Forward()
        rhs_expr << base_expr + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(rhs_expr)
    
        # Pattern for equation parsing
        return rhs_expr
        
    def __createParsePatternForVariableDefining(self):
        variable = Word(alphas + nums)
        return variable + Suppress(restOfLine)
        
    def createParsePattern(self, *args):
        length = len(args)
        if length == 0:
            return self.__createParsePatternForVariableDefining()
        elif length == 1:
            raise AttributeError("Method createParsePattern() didn't take one argument!")
        elif length == 2:
            return self.__createParsePatternForMathFunction(args[0], args[1])
        elif length == 3:
            # print("ppc.createParsePattern: diffEq used")
            return self.__createParsePatternForDiffEquation(args[0], args[1], args[2])
        elif length == 4:
            print("ppc.createParsePattern: diffEq delay used")
            return self.__createParsePatternForDiffEquation(args[0], args[1], args[2], delays=args[3])
        else:
            raise AttributeError("Method createParsePattern() didn't take four or more arguments!")

class MathExpressionParser:
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
        
    def parseMathExpression(self, mathExpressionForParsing, *args):
        controller = CorrectnessController()
        controller.emptyControl(mathExpressionForParsing)
        controller.controlOperators(mathExpressionForParsing)
        controller.controlBrackets(mathExpressionForParsing)
        
        length = len(args)
        if length < 2 or length  > 4:
            raise AttributeError("Method parseMathExpression() takes at least three arguments and didn't take five or more arguments!")
        
        ppc = ParsePatternCreater()
        if length != 4:
            parsePattern = ppc.createParsePattern(*args)
        else:
            parsePattern = ppc.createParsePattern(*args)

        # print("parsePattern=")
        # print(parsePattern)
        
        # print("mathExpressionForParsing=")
        # print(mathExpressionForParsing)

        parsedExpression = parsePattern.parseString(mathExpressionForParsing).asList()
        controller.controlPowers(parsedExpression)
        self.__concatPower(parsedExpression)
        if length != 4:
            controller.controlDerivatives(parsedExpression, args[-1])
       
        # print("parsedExpression=")
        # print(parsedExpression)

        return parsedExpression

    def getVariableList(self,equationStringList):
        ppc = ParsePatternCreater()
        parsePattern = ppc.createParsePattern()
        controller = CorrectnessController()
        
        variableList = list([])
        for equationString in equationStringList:
            if equationString.find("=") == -1:
                raise SyntaxError("Some equation in the system either doesn't contain the symbol '=' or is an empty string!")
            controller.emptyControl(equationString)
            variableList.extend(parsePattern.parseString(equationString).asList())
        return variableList
    
