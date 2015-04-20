from equationParser import Parser

class DerivativeHandler:
    def orderOfSystem(self,estrList,parList):
        parser = Parser()
        parsedStrList = parser.getRhsLst(estrList,parList)
        order = list([])
        for equation in parsedStrList:
            for element in equation:
                if element[0] == 'D[':
                    order.extend([int(element[6])])
        return max(order)