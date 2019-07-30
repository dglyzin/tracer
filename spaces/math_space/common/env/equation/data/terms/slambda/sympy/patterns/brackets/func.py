import sympy


class Func():
    
    '''for f (left=f right=))'''
    
    def __init__(self, net):
        self.net = net
        self.gnet = self.net.net

        # this meen left_term.name == 'f'
        # right_node.name == ')'
        self.id = 'l:f|r:)'

    def __call__(self, node_br):
        
        '''Add cpp out to brackets'''

        left_node = node_br[0]
        right_node = node_br[-1]

        # get node data:
        self.get_node_data(node_br)
        
        # transform to lambda:
        out = self.slambda()

        self.gnet.set_slambda(left_node, out)

    def get_node_data(self, node_br):

        '''Used for fill local data'''

        left_node = node_br[0]
        right_node = node_br[-1]

        args_node = node_br[1]
        self.args_count = len(args_node)
        '''
        if args_count > 1:
            raise(BaseException("term func for lambda_sympy not"
                                + " supported more then one argument"))
        '''
        # FOR left_node (sin():
        if 'variable' in left_node.args:
            # for func like f, g, h value must exist
            # substituted with subs:
            self.func_name = left_node.args['variable']['value']
        else:
            # for func like sin, cos, exp:
            # func = left_node.name.lex[0][:-1]
            self.func_name = self.gnet.get_term_value(left_node)[:-1]
        # END FOR
        
    def slambda(self):
        
        # this func=self.func used to prevent oweriding of different
        # terms, that used same Func instance.
        # so it's point at differ objects because of it's copy
        # objects (not pointer) in expresion func = self.func:
        return(lambda *A, func=self.func_name: sympy.simplify(func)(*A))
