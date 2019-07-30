class DotTranspose():

    '''Generate cpp data for dot:
    .t .t() -> .transpose()'''

    def __init__(self, net):
        self.net = net
        self.id = 'dot_transpose'

    def get_lambda(self, node):
    
        val = self.net.get_term_value(node)

        if '.t' in val:
            out = lambda X: X.transpose()
        else:
            out = None
        # print("from lambda diff")

        return(out)
        # out = "sympy.diff(%s, %s, %s)" % (var, free_var, order)
