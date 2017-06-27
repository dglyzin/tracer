class CppOutsForTerms():
    def __init__(self, params):
        self.params = params

    def get_out_for_term(self, termName):
        '''
        DESCRIPTION:
        termName - name of term like termVarsPoint1D
        '''
        methods = self.__class__.__dict__
        for methodName in methods.keys():
            methodTermName = methodName.split('_')[-1]
            if methodTermName == termName:
                return(methods[methodName](self))

    def get_out_for_termVarsPoint(self):
        
        if self.params.dim == '1D':
            return(self.get_out_for_termVarsPoint1D())
        elif self.params.dim == '2D':
            return(self.get_out_for_termVarsPoint2D())

    def get_out_for_termVarsPoint1D(self):
            return('source[0][arg2*D'+'arg1'+'M1*CELLSIZE]')
        
    def get_out_for_termVarsPoint2D(self):
        blockNumber = self.params.blockNumber
        return(('source[0][(arg2*D'+'arg1'+'M1'
                + '+'
                + 'arg4'+'*D'
                + 'arg3'+'M1*Block'
                + str(blockNumber)
                + 'StrideY)*CELLSIZE]'))

    def get_out_for_termVarsPointDelay(self):
        
        if self.params.dim == '1D':
            return(self.get_out_for_termVarsPoint1DDelay())
        elif self.params.dim == '2D':
            return(self.get_out_for_termVarsPoint2DDelay())

    def get_out_for_termVarsPoint1DDelay(self):
            return('source[arg1][arg3*D'+'arg2'+'M1*CELLSIZE]')
        
    def get_out_for_termVarsPoint2DDelay(self):
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

