# -*- coding: utf-8 -*-
import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.equationParser import MathExpressionParser
else:
    from equationParser import MathExpressionParser


class DelayHandler:
    
    def determineDelay(self,estrList,parList,indepVariableList):
        parser = MathExpressionParser()
        variables = parser.getVariableList(estrList)
        parsedStrList = list([])
        for equation in estrList:
            parsedStrList.extend([parser.parseMathExpression(equation,variables,parList,indepVariableList)])
        
        delay_set = set() # we need set, because we must collect only unique delays        
        for equation in parsedStrList:
            for i, term in enumerate(equation):
                # minus 5 because we need a place for delay with the following syntax:
                # [variable], [left round bracet], [time var], [minus sign], [delay value], [right round bracet]
                if term in variables and i < len(equation)-5:
                    # check syntax
                    if (equation[i+1] == '('
                    and equation[i+2] == 't'
                    and equation[i+3] == '-'
                    and equation[i+4].isdigit()
                    and equation[i+5] == ')'):
                        delay_set.add(int(equation[i+4]))
                       
        return sorted(delay_set)
