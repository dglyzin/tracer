class Params():
    def __init__(self):
        # for comment before each central function
        self.hatCf = dict()
        
        # for name of central functions
        self.namesCf = dict()
        pass
    
    def set_hat_for_all_cf(self, blockNumber):
        self.cf_hat_common = ('\n//========================='
                              + 'CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER '
                              + str(blockNumber)
                              + '========================//\n\n')
    
    def set_stride_map(self, blockNumber):
        self.strideMap = dict()
        for var in 'xyz':
            self.strideMap[var] = ('Block' + str(blockNumber)
                                   + 'Stride' + var.upper())
        
    def get_hat_for_cf(self, blockNumber, eqNumber, dim):
        text = ('//'+str(eqNumber)
                + ' central function for '
                + str(dim)
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

    def get_cf_signature(self, blockNumber, name, strideList):

        signatureStart = 'void ' + name + '(double* result, double** source, double t,'
        signatureMiddle = ''
        for var in 'xyz':
            signatureMiddle = signatureMiddle + ' int idx' + var.upper() + ','
        signatureEnd = ' double* params, double** ic){\n'

        signature = signatureStart + signatureMiddle + signatureEnd
          
        idx = '\t int idx = ('
        for var in 'xyz':
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
