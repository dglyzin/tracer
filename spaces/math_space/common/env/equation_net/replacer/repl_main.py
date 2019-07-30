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

    def load_patterns_source(self, dialect_name, brackets=False):
        if dialect_name == "cpp":
            patterns = (self.cpp.gen.patterns_editor
                        .load_patterns_source("cpp", brackets=brackets))
        elif dialect_name == "sympy":
            patterns = (self.sympy.gen.patterns_editor
                        .load_patterns_source("sympy", brackets=brackets))
        else:
            print("no such dialect")
        return(patterns)

    def remove_patterns(self, dialect_name, term_names):
        if dialect_name == "cpp":
            self.cpp.gen.patterns_editor.remove_patterns("cpp", term_names)
        elif dialect_name == "sympy":
            self.sympy.gen.patterns_editor.remove_patterns("sympy", term_names)
        else:
            print("no such dialect")

    def set_pattern(self, dialect_name, term_name, code, brackets=False):
        if dialect_name == "cpp":
            self.cpp.gen.patterns_editor.set_pattern("cpp", term_name,
                                                     code, brackets=brackets)
        elif dialect_name == "sympy":
            self.sympy.gen.patterns_editor.set_pattern("sympy", term_name,
                                                       code, brackets=brackets)
        
