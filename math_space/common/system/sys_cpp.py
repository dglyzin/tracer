class sysCpp():
    def __init__(self, net):
        self.net = net

    def parse(self):
        for eq in self.net.eqs:
            eq.parse()

    # FOR params:
    def set_default(self):
        for eq in self.net.eqs:
            eq.set_dim(dim=2)
            eq.set_blockNumber(blockNumber=0)

            eq.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])

            coeffs_to_indexes = [('a', 0), ('b', 1), ('c', 2), ('r', 3)]
            eq.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

            eq.set_diff_type(diffType='pure',
                             diffMethod='common')
            eq.set_shape(shape=[30, 31])

    def set_dim(self, dim):
        for eq in self.net.eqs:
            eq.set_dim(dim=dim)
            
    def set_blockNumber(self, blockNumber):
        for eq in self.net.eqs:
            eq.set_blockNumber(blockNumber=blockNumber)
        
    def set_vars_indexes(self, vars_to_indexes=[('U', 0), ('V', 1)]):
        for eq in self.net.eqs:
            eq.set_vars_indexes(vars_to_indexes=vars_to_indexes)
        
    def set_diff_type_common(self, diffType='pure', diffMethod='common'):
        for eq in self.net.eqs:
            eq.set_diff_type(diffType=diffType, diffMethod=diffMethod)

    def set_diff_type_special(self, diffType='pure', diffMethod='common',
                              side=0, func='0'):
        for eq in self.net.eqs:
            eq.set_diff_type(diffType=diffType, diffMethod=diffMethod,
                             side=side, func=func)

    def set_diff_type_ic(self, side_num, firstIndex, secondIndex):
        for eq in self.net.eqs:
            eq.set_diff_type(diffType="pure",
                             diffMethod="interconnect",
                             side=side_num,
                             firstIndex=firstIndex,
                             secondIndexSTR=secondIndex)
    
    def set_shape(self, shape=[3, 3]):
        '''For bound like "V(t-1.1,{x,1.3}{y, 5.3})".
        Input:
        point=[3, 3]'''
        for eq in self.net.eqs:
            eq.set_shape(shape=shape)
        
    def set_coeffs_indexes(self, coeffs_to_indexes=[('a', 0), ('b', 1),
                                                    ('c', 2), ('r', 3)]):

        '''map coeffs ot it's index
        like (a,b)-> (params[+0], params[+1])

        Input:
        coeffs_to_indexes=[('a', 0), ('b', 1)]
        '''
        for eq in self.net.eqs:
            eq.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)
    # END FOR
