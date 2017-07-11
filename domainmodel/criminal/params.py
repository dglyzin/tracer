class Params():
    '''
    DESCRIPTION:
    If string for cpp out (from cppOutsForTerms.py)
    contain some params or
    If actions in Actions.py contain some params
    that params must be there initiated.
    Or they must be added in parser.__init__ method in
    according section.
    '''
    def __init__(self):
        # for comment before each central function
        self.hatCf = dict()
        
        # for name of central functions
        self.namesCf = dict()

    def init_params_general(self, blockNumber, dim):
        # parameters fill
        self.dim = dim
        if blockNumber is not None:
            self.blockNumber = blockNumber
        else:
            self.blockNumber = 0
        self.dim = dim
            
    def set_hat_for_all_cf(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        '''
        self.cf_hat_common = ('\n//========================='
                              + 'CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER '
                              + str(blockNumber)
                              + '========================//\n\n')
    
    def set_stride_map(self, blockNumber):
        '''
        USED FUNCTIONS:
        blockNumber
        self.dim
        '''
        self.strideMap = dict()
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            self.strideMap[var] = ('Block' + str(blockNumber)
                                   + 'Stride' + var.upper())
        
    def get_hat_for_cf(self, blockNumber, eqNumber):
        '''
        USED FUNCTIONS
        blockNumber
        equationNumber
        self.dim
        '''
        text = ('//'+str(eqNumber)
                + ' central function for '
                + str(self.dim)
                + 'd model for block with number '
                + str(blockNumber)
                + '\n')

        self.hatCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_name(self, blockNumber, eqNumber):
        text = ('Block' + str(blockNumber)
                + 'CentralFunction'
                + str(eqNumber))  # numsForEquats[num]
        self.namesCf[(blockNumber, eqNumber)] = text
        return(text)

    def get_cf_signature(self, blockNumber, name):
        '''
        USED FUNCTIONS:
        self.dim
        blockNumber
        name - function name
        '''
        signatureStart = 'void ' + name + '(double* result, double** source, double t,'
        signatureMiddle = ''
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            signatureMiddle = signatureMiddle + ' int idx' + var.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'

        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ('
        vars = 'xyz'
        for i in range(int(self.dim[0])):
            var = vars[i]
            idx = idx + ' + idx' + var.upper() + ' * ' + self.strideMap[var]
        idx = idx + ') * Block' + str(blockNumber) + 'CELLSIZE;\n'
        
        return list([signature, idx])
    
    def rest(self):
        delays = []
                
        equationRightHandSide = parser.parseMathExpression(equationString, variables,
                                                           self.params, self.userIndepVars,
                                                           delays)
        function.extend([
            b.generateRightHandSideCodeDelay(blockNumber, variables[i],
                                             equationRightHandSide,
                                             self.userIndepVars, variables,
                                             self.params, list(),
                                             delays)])
        # for setDomain
        if len(delays) > 0:
            self.delays.extend(delays)
            
        function.extend(['}\n\n'])
        
        return ''.join(function), arrWithFuncName
