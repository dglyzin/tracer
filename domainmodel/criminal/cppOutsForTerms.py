class CppOutsForTerms():
    def __init__(self, params):
        self.params = params

    def get_out_for_term(self, termName):
        
    def get_out_for_termVarsPoint1D(self):
            return('source[arg1][arg3*D'+'arg2'+'M1*CELLSIZE]')
        
    def get_out_for_termVarsPoint2D(self):
        blockNumber = self.params.blockNumber
        return(('source[arg1][(arg3*D'+'arg2'+'M1'
                + '+'
                + 'arg5'+'*D'
                + 'arg4'+'M1*Block'
                + str(blockNumber)
                + 'StrideY)*CELLSIZE]'))

    def get_out_for_termVarSimple(self):
                    
        return('source['
               + 'arg1'  # delay
               + '][idx + '
               + 'arg2'  # str(varIndex)
               + ']')

    def get_out_for_termParam(self):
        return('params['
               + 'arg1'  # str(parIndex)
               + ']')

    def get_out_for_termBinary(self):
        return(' '
               + 'arg1'  # expressionList
               + ' ')

    def get_out_for_termFunc(self):
        return('arg1')  # expressionList

