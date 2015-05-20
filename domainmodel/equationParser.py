# -*- coding: utf-8 -*-
from pyparsing import Literal, Word, nums, alphas, Group, Forward, Optional, OneOrMore, Suppress, restOfLine, ZeroOrMore

class CorrectnessController:

    def controlBrackets(self, stringForControl):
        count = 0
        for char in stringForControl:
            if char == '(':
                count = count + 1
            elif char == ')':
                count = count - 1
        return count
    
    def controlOperators(self, stringForControl):
        correct = True
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
                correct = False
                break
        return correct

    def controlPowers(self, parsedStringForControl):
        for lst in parsedStringForControl:
            if lst[0] == '^':
                power = lst[1:]
                if not power.isnumeric():
                    return -1
        return 1
    
    def controlDerivatives(self, parsedStringForControl, independentVariableList):
        for expressionList in parsedStringForControl:
            if expressionList[0] == 'D[':
                listOfInputedVars = list([])
                for i,symbol in enumerate(expressionList):
                    if symbol == '{':
                        if expressionList[i+1] not in independentVariableList:
                            return 1
#                         elif expressionList[i+1] in listOfInputedVars:
#                             return 2
                        elif int(expressionList[i+3]) == 0:
                            return 3
                        else:
                            listOfInputedVars.extend([expressionList[i+1]])
        return 0

class ParsePatternCreater:
    
    def __createParsePatternForDiffEquation(self, variableList, parameterList, indepVariableList):
        real = Word(nums + '.')
        integer = Word(nums)
        
        parameter = Literal(parameterList[0])
        for par in parameterList:
            parameter = parameter^Literal(par)
            
        variable = Literal(variableList[0])
        for var in variableList:
            variable = variable^Literal(var)
        
        indepVariable = Word(alphas + nums)
        
        order = '{' + indepVariable + ',' + integer + '}'
        derivative = 'D['+ variable + ','+ order + ZeroOrMore(',' + order) + ']'
    
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
        return Suppress(variable + "'" + '=') + rhs_expr
        
    def __createParsePatternForMathFunction(self, parameterList, independentVariableList):
        real = Word(nums + '.')
        
        parameter = Literal(parameterList[0])
        for par in parameterList:
            parameter = parameter^Literal(par)
        
        indepVariable = Literal(independentVariableList[0])
        for var in independentVariableList:
            indepVariable = indepVariable^Literal(var)
    
        funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')
        unaryOperation = Literal('-')^funcSignature
        binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')
        operand = real^indepVariable^parameter
    
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
            return self.__createParsePatternForDiffEquation(args[0], args[1], args[2])
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
        length = len(args)
        if length < 2 or length  > 3:
            raise AttributeError("Method parseMathExpression() takes at least three arguments and didn't take five or more arguments!")
        
        ppc = ParsePatternCreater()
        parsePattern = ppc.createParsePattern(*args)
        
        controller = CorrectnessController()
                   
        boundaryCount = controller.controlBrackets(mathExpressionForParsing)
        if boundaryCount < 0:
            raise SyntaxError('Either too more closing brackets or there is a lack of opening brackets in input function !')            
        elif boundaryCount > 0:
            raise SyntaxError('Either too more opening brackets or there is a lack of closing  brackets in input function !')
            
        parsedExpression = parsePattern.parseString(mathExpressionForParsing).asList()
        self.__concatPower(parsedExpression)
        if not controller.controlPowers(parsedExpression):
            raise SyntaxError('A power is not an integer!')
        
        derivativeControlResult = controller.controlDerivatives(parsedExpression, args[-1])
        if derivativeControlResult == 1:
            raise SyntaxError("Error in inputing of some derivative: independent variable, in which partial derivative should be calculated, is absent in list of independent variables!")
        elif derivativeControlResult == 2:
            raise SyntaxError("Error in inputing of some derivative: duplication of independent variable, in which derivative should be calculate!")
        elif derivativeControlResult == 3:
            raise SyntaxError("Error in inputing of some derivative: derivative should have positive order!")
        
        strForControl = ''
        for element in parsedExpression:
            strForControl = strForControl + ''.join(element)
        if not controller.controlOperators(strForControl):
            raise SyntaxError('Some binary operators are located uncorrectly in input function !')
        
        return parsedExpression

    def getVariableList(self,equationStringList):
        ppc = ParsePatternCreater()
        parsePattern = ppc.createParsePattern()
        
        variableList = list([])
        for equationString in equationStringList:
            variableList.extend(parsePattern.parseString(equationString).asList())
        return variableList
    