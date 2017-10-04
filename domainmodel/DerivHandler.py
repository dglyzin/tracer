# -*- coding: utf-8 -*-
import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.equationParser import MathExpressionParser
else:
    from equationParser import MathExpressionParser


class DerivativeHandler:
    
    def orderOfSystem(self,estrList,parList,indepVariableList):
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        parsedStrList = list([])
        for equation in estrList:
            parsedStrList.extend([parser.parseMathExpression(equation,variables,parList,indepVariableList)])
            
        orderList = list([0])
        for equation in parsedStrList:
            for expressionList in equation:
                if expressionList[0] == 'D[':
                    order = 0
                    for i,symbol in enumerate(expressionList):
                        if symbol == '{':
                            order = order + int(expressionList[i+3])
                    orderList.extend([order])
                    
        return max(orderList)
