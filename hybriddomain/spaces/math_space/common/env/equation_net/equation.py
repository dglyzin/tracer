import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
# print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from env.equation_net.parser.parser_main import EqParser
from env.equation_net.replacer.repl_main import EqReplacer
from env.equation_net.net.eq_net import NetEditor

'''
from env.equation.parser.parser_main import EqParser
from env.equation.args.args_main import EqArgs
from env.equation.slambda.slambda_main import EqSlambda
from env.equation.sampling.eq_sampling import EqSampling
from env.equation.cas.cas_main import CAS
'''

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('tests.tester.tests_common')

# if using directly uncoment that:
# create logger
import logging

log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)

logger.debug('sys.path[0]')
logger.debug(sys.path[0])


class Equation():
    
    def __init__(self, sent, db=None, trace=0):

        '''db had been initiated with path and ``load_all_tables``
        had been used (see also ``parser_main.EqParser.__init__``
        where it used)'''

        if db is not None:
            self.db = db
        else:
            from gui.web.model.model_main import TokenizerDB
            self.db = TokenizerDB()
            # self.path_db = "env/equation_net/data/terms/input/demo_dialect.db"
            self.db.change_dialect_db("eqs")

        self.parser = EqParser(self)
        self.net_editor = NetEditor(self)
        self.replacer = EqReplacer(self)

        # Init nodes content:
        self.replacer._init_node_content()
        
        self.sent = sent

    def get_all_nodes(self):
        try:
            # ask for networkx nodes names
            nodes = self.net_out.node.keys()
        except AttributeError:
            print(("has no eq_net yiet,"
                   + " use parser.parse first"))
            nodes = None

        return(nodes)

    def show_cpp(self):
        return("".join(self.net_editor.flatten('cpp')))

    def show_original(self):
        
        '''net_editor.flatten work only after parser.parse
        (because net will be set to replacer only after parsing)'''

        use_flatten = False
        try:
            out = self.net_out
            use_flatten = True
        except AttributeError:
            use_flatten = False

        if use_flatten:
            out = self.net_editor.flatten("original")
        else:
            out = self.sent
        print(out)

    def __repr__(self):
        out = self.sent
        return(out)

    def show_lex_out(self):
        print(self.lex_out)
        # print(self.eq_tree.show_original())
    
    def show_cyk_out(self):
        print(self.cyk_out)
        # print(self.eq_tree.show_original())
        
    def show_tree_original(self):
        print(self.net_out.node)
        # print(self.eq_tree.show_original())

    def show_net_original(self):
        print(self.net_out.node)

    def show_net_json_original(self):
        print(self.json_out)
    
    
if __name__ == "__main__":

    sent = "U'=a*(D[U,{x,2}]+ D[U,{y,2}])"
    print("\noriginal:")
    print(sent)
    
    eq = Equation(sent)
    eq.parser.parse()
    eq.replacer.cpp.editor.set_default()
    eq.replacer.cpp.make_cpp()
    eq.show_cpp()

    print("\nresult:")
    print(eq.show_cpp())

