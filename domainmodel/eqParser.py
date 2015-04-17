# -*- coding: utf-8 -*-
from pyparsing import *

#Создан для отслеживания того, что в уравнении
#присутствует одинаковое количество открывающих и закрывающих скобок.
def boundaryController(estr):
    count = 0
    for char in estr:
        if char == '(':
            count = count + 1
        elif char == ')':
            count = count - 1
    return count

#Создан для отслеживания того, что в уравнении
#никакие два бинарных оператора не стоят рядом.
def correctOperationSequence(estr):
    correct = True
    operationList = list(['+','-','*','/','^'])
    length = len(estr)
    for i,char in enumerate(estr):
        if char in operationList and ( (i > 1 and estr[i-1] in operationList) or (i < length - 2 and estr[i+1] in operationList)):
            correct = False
            break
    return correct

#Из элементов массива типа '^','3' делает один элемент '^3'
def concatPower(lst):
    index = 0
    while lst.count('^') > 0:
        index = lst.index('^',index)
        power = lst[index + 1]
        lst.pop(index)
        lst.pop(index)
        power = '^' + power
        lst.insert(index,power)

def getRhsLst(estrList,parList):
    real = Word(nums + '.')
    integer = Word(nums)
    
    parameter = Literal(parList[0])
    for par in parList:
        parameter = parameter^Literal(par)
        
    varLst = getLhsList(estrList)
    variable = Literal(varLst[0])
    for var in varLst:
        variable = variable^Literal(var)
        
    indepVariable = Word(alphas + nums)
    derivative = 'D['+ variable + ','+ '{' + indepVariable + ',' + integer + '}' + ']'

    funcSignature = Literal('exp')^Literal('sin')^Literal('cos')^Literal('tan')^Literal('sinh')^Literal('tanh')^Literal('sqrt')^Literal('log')
    unaryOperation = Literal('-')^funcSignature
    binaryOperation = Literal('+')^Literal('-')^Literal('*')^Literal('/')^Literal('^')
    operand = variable^parameter^Combine(derivative)^real

    recursiveUnaryOperation = Forward()
    recursiveUnaryOperation << (Literal('(')^unaryOperation) + Optional(recursiveUnaryOperation)
    base_expr = Forward()
    base_expr << Optional(recursiveUnaryOperation) + operand + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(base_expr)
    rhs_expr = Forward()
    rhs_expr << base_expr + Optional(OneOrMore(')')) + Optional(binaryOperation) + Optional(rhs_expr)

    #Уравнение парсится по следующему шаблону
    equation_expression = Suppress(variable + "'" + '=') + rhs_expr

    rhsLst = list([])
    for eq in estrList:
        if not correctOperationSequence(eq):
            raise SyntaxError(u'В уравнении ' + eq + u' несколько бинарных операций стоят рядом, что недопустимо!')            
        boundaryCount = boundaryController(eq)
        if boundaryCount < 0:
            raise SyntaxError(u'В уравнении ' + eq + u' где-то либо имеются лишние закрывающие скобки, либо отсутствует некотрое количество открывающих!')            
        elif boundaryCount > 0:
            raise SyntaxError(u'В уравнении ' + eq + u' где-то либо имеются лишние открывающие скобки, либо отсутствует некотрое количество закрывающих!')            
        rhsLst.extend([equation_expression.parseString(eq).asList()])

    #Для создания по этому массиву сишной функции удобно, чтобы выражение типа ^3 было единой строкой!
    for parsedEq in rhsLst:
        concatPower(parsedEq)
    return rhsLst

def getLhsList(estrList):
    variable = Word(alphas + nums)
    lhs_expression = variable + Suppress(restOfLine)
    out = list([])
    for eq in estrList:
        out.extend(lhs_expression.parseString(eq).asList())
    return out

def orderOfSystem(estrList,parList):
    parsedStrList = getRhsLst(estrList,parList)
    order = list([])
    for equation in parsedStrList:
        for i,element in enumerate(equation):
            if element[0] == 'D' and len(element) > 1 and element[1] == '[':
                order.extend([int(element[7])])
    return max(order)
