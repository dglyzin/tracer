from env.equation.data.terms.slambda.sympy.replacer_lambda_sympy import LambdaSympyGen
import inspect
import sympy


def slambda_attr_extractor(node):
    # print("######")
    # print(node)
    # print(node.name)
    # print("######")
    # print(node.name.lex[0])
    
    try:
        node.slambda.sympy
    except AttributeError:
        return(None)
    # print(node.slambda.sympy)
    # print(inspect.getargspec(node.slambda.sympy).args)
    return(node.slambda.sympy)


class SlambdaSympy():
    
    def __init__(self, net):
        self.net = net
        self.gnet = net.net

    def lambdify_sem(self):

        '''Add semantic for sympy to nodes in self.gnet.eq_tree'''

        gen = LambdaSympyGen()
        self.gnet.eq_tree_lambda_sympy = self.gnet.tree.map_out(gen)
    
    def lambdify(self, tree=None):
        out = self.net.lambdify(slambda_attr_extractor, tree)
        self.gnet.eq_lambda_sympy = out
        self.gnet.eq_lambda_sympy_call = out()
        return(out)
        
    def lambdify_call(self, tree=None):
        out = self.net.lambdify_call(slambda_attr_extractor, tree)
        self.gnet.eq_lambda_sympy_call = out
        return(out)
        
    def show_sympy_lambda(self):
        sympy.printing.pprint(self.gnet.eq_lambda_sympy_call)
