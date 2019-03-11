from env.equation_net.replacer.cpp.cpp_main import ReplCpp
from env.equation_net.replacer.sympy.sympy_main import ReplSympy


class EqReplacer():

    '''Convert tree's nodes to some out (cpp, sympy)'''

    def __init__(self, net):
        self.net = net
        self.cpp = ReplCpp(net)
        self.sympy = ReplSympy(net)

    def _init_node_content(self):

        '''Method used after net initialization'''

        self.cpp.editor._init_node_content()
