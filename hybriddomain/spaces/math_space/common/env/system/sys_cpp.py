class sysCpp():
    def __init__(self, net):
        self.net = net

    def parse(self):
        for eq in self.net.eqs:
            eq.parser.parse()

    def gen_cpp(self):
        self.cpp_out = []
        for eq in self.net.eqs:
            
            self.cpp_out.append(eq.replacer.cpp.make_cpp())

    # FOR params:
    def set_default(self):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor

            editor.set_dim(dim=2)
            editor.set_blockNumber(blockNumber=0)

            editor.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])

            coeffs_to_indexes = [('a', 0), ('b', 1), ('c', 2), ('r', 3)]
            editor.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

            editor.set_diff_type(diffType='pure',
                                 diffMethod='common')
            editor.set_shape(shape=[30, 31])

    def set_dim(self, dim):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_dim(dim=dim)
            
    def set_blockNumber(self, blockNumber):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_blockNumber(blockNumber=blockNumber)
        
    def set_vars_indexes(self, vars_to_indexes=[('U', 0), ('V', 1)]):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_vars_indexes(vars_to_indexes=vars_to_indexes)
        
    def set_diff_type_common(self, diffType='pure', diffMethod='common'):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_diff_type(diffType=diffType, diffMethod=diffMethod)

    def set_diff_type_special(self, diffType='pure', diffMethod='common',
                              side=0, func='0'):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_diff_type(diffType=diffType, diffMethod=diffMethod,
                                 side=side, func=func)

    def set_diff_type_ic(self, side_num, firstIndex, secondIndex):
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_diff_type(diffType="pure",
                                 diffMethod="interconnect",
                                 side=side_num,
                                 firstIndex=firstIndex,
                                 secondIndexSTR=secondIndex)
    
    def set_shape(self, shape=[3, 3]):
        '''For bound like "V(t-1.1,{x,1.3}{y, 5.3})".
        Input:
        point=[3, 3]'''
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_shape(shape=shape)
        
    def set_coeffs_indexes(self, coeffs_to_indexes=[('a', 0), ('b', 1),
                                                    ('c', 2), ('r', 3)]):

        '''map coeffs ot it's index
        like (a,b)-> (params[+0], params[+1])

        Input:
        coeffs_to_indexes=[('a', 0), ('b', 1)]
        '''
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

    def set_free_var_prefix(self, free_var_prefix=(lambda val, state: "idx"+val.upper())):
    
        ''' x |-> params["free_var_prefix"](x, self)

        Input:
        free_var_prefix = lambda val, state: "idx"+val.upper()
        '''
        for eq in self.net.eqs:
            editor = eq.replacer.cpp.editor
            editor.set_free_var_prefix(free_var_prefix=free_var_prefix)

    # END FOR
