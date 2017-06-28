class CppOutsForTerms():
    '''
    DESCRIPTION:
    If pattern (termDemo) should contain
    cpp out
    then
    there should exist function
    (get_out_for_termDemo)
    and 
    if this function use some
    parameters, they must exist
    and initiated in params before.
    (all that happened in Parser.py)
    '''
    # use varIndexs for all 
    # CppOutsForTerms objects
    dataTermVarSimple = {'varIndexs': []}

    def __init__(self, params):
        self.params = params
        
        self.dataTermVarsPoint = []
        self.dataTermVarsPointDelay = []
        self.dataTermVarSimpleLocal = {'delays': [],
                                       'varIndexs': []}

    def get_out_for_term(self, termName):
        '''
        DESCRIPTION:
        Find out for term (termDemo) with termName 
        (from Patterns.py). For that method with name
        get_out_for_termDemo must exists.

        INPUT:
        termName - name of term like termVarsPoint1D
        '''
        methods = self.__class__.__dict__
        for methodName in methods.keys():
            methodTermName = methodName.split('_')[-1]
            if methodTermName == termName:
                return(methods[methodName](self))

    def get_out_for_termVarsPoint(self):
        '''
        DESCRIPTION:
        For patterns like
        U(t,{x,0.7})
        U(t,{x,0.7}{y,0.3})
        '''
        if self.params.dim == '1D':
            return(self.get_out_for_termVarsPoint1D())
        elif self.params.dim == '2D':
            return(self.get_out_for_termVarsPoint2D())

    def get_out_for_termVarsPoint1D(self):
        '''
        DESCRIPTION:
        For patterns like U(t,{x,0.7})
        '''
        blockNumber = self.params.blockNumber
        return('source[0][arg1'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE]')
        
    def get_out_for_termVarsPoint2D(self):
        '''
        DESCRIPTION:
        For U(t,{x,0.7}{y,0.3})
        '''
        blockNumber = self.params.blockNumber
        return(('source[0][(arg1'
                + '+'
                + 'arg2'+'*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE]'))

    def get_out_for_termVarsPointDelay(self):
        '''
        DESCRIPTION:
        For patterns like U(t-1.3,{x,0.7}{y,0.3})
        '''
        if self.params.dim == '1D':
            return(self.get_out_for_termVarsPoint1DDelay())
        elif self.params.dim == '2D':
            return(self.get_out_for_termVarsPoint2DDelay())

    def get_out_for_termVarsPoint1DDelay(self):
        blockNumber = self.params.blockNumber
        return('source[arg_T_var][arg_X_var'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE'
               + '+'+'arg_varIndex'+']')
        
    def get_out_for_termVarsPoint2DDelay(self):
        blockNumber = self.params.blockNumber
        return(('source[arg_T_var][(arg_X_var'
                + '+'
                + 'arg_Y_var'+'*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE'
                + '+'+'arg_varIndex' + ']'))

    def get_out_for_termVarSimple(self):
        '''
        DESCRIPTION:
        varIndex usage:
        source[][idx+0] - x
        source[][idx+1] - y
        source[][idx+2] - z
        
        '''
        return('source['
               + 'arg1'  # delay
               + '][idx + '
               + 'arg_varIndex'  # str(varIndex)
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

