class Editor():
    
    def __init__(self, net):
        self.net = net

    def _init_node_content(self):
        self.cpp_replacer = self.net.replacer.cpp.gen

    # FOR set out cpp parameters:

    def set_default(self):
        self.set_dim(dim=2)
        self.set_blockNumber(blockNumber=0)

        self.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])

        coeffs_to_indexes = [('a', 0), ('b', 1),
                             ('c', 2), ('r', 3), ('d', 4)]
        self.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

        self.set_diff_type(diffType='pure',
                           diffMethod='common')
        self.set_shape(shape=[30, 30])

    def set_dim(self, **kwargs):

        '''dim=2'''

        self.cpp_replacer.set_dim(**kwargs)
        # self.net.sympy_replacer.set_dim(**kwargs)

    def set_blockNumber(self, **kwargs):

        '''blockNumber=0'''

        self.cpp_replacer.set_blockNumber(**kwargs)

    def set_vars_indexes(self, **kwargs):

        ''' Shift index for variable:
        like (U,V)-> (source[+0], source[+1])

        Input:
        vars_to_indexes=[('U', 0), ('V', 1)]
        '''

        self.cpp_replacer.set_vars_indexes(**kwargs)
        
    def set_diff_type(self, **kwargs):

        '''
        Inputs:
           diffType="pure", diffMethod="common"

           diffType="pure", diffMethod="borders",
           side=0, func="sin(x)"

           diffType="pure", diffMethod="interconnect",
           side=0, firstIndex=0, secondIndexSTR=1

        ::

          ***x->
          *  
          |  ---side 2---
          y  |          |
             s          s
             i          i
             d          d
             e          e
             0          1
             |          |
             ---side 3---
        '''

        self.cpp_replacer.set_diff_type(**kwargs)

    def set_shape(self, **kwargs):

        '''For bound like "V(t-1.1,{x,1.3}{y, 5.3})".

        Input:
        shape=[3, 3]'''

        self.cpp_replacer.set_shape(**kwargs)
        
    def set_coeffs_indexes(self, **kwargs):

        '''map coeffs ot it's index
        like (a,b)-> (params[+0], params[+1])

        Input:
        coeffs_to_indexes=[('a', 0), ('b', 1)]
        '''
        self.cpp_replacer.set_coeffs_indexes(**kwargs)

    def set_free_var_prefix(self, **kwargs):

        ''' x |-> params["free_var_prefix"](x, self)

        Input:
        free_var_prefix = lambda val, state: "idx"+val.upper()
        '''
        self.cpp_replacer.set_free_var_prefix(**kwargs)

    # END FOR
