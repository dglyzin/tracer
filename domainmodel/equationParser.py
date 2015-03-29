# -*- coding: utf-8 -*-
from pyparsing import *
import numpy as np

#Определения элементов парсинга
real = Word(nums + '.')
integer = Word(nums)
parameter = Word(alphas + nums)
variable = Word(alphas + nums)
indepVariable = Word(alphas + nums)
operation = Word('+-*/^=')
derivative = 'D['+ variable + ','+ '{' + indepVariable + ',' + integer + '}' + ']'
exp = Literal('exp')
sin = Literal('sin')
cos = Literal('cos')
tan = Literal('tan')
ctan = Literal('ctan')
sinh = Literal('sinh')
cosh = Literal('cosh')
tanh = Literal('tanh')
ctanh = Literal('ctanh')
elementaryFunction = sin^cos^exp^tan^ctan^cosh^sinh^tanh^ctanh

#Уравнение парсится по следующему шаблону
exprForm1 = Optional('(') + (variable^real^parameter^elementaryFunction^derivative) + Optional(')') + Optional(operation) + Optional(')')
expression = Suppress(variable + "'" + '=') + OneOrMore(exprForm1)

#estr -- строка, сформированная по установленному в .json правилу
def parseEquation(estr):
    return expression.parseString(estr)

def orderOfEquation(estr):    
    parsedStr = expression.parseString(estr)
    order = np.array([])
    for i,element in enumerate(parsedStr):
        if element == 'D[':
            order = np.hstack((order,np.array([int(parsedStr[i+6])])))
    return int(order.max())
