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

from env.clause.parser.parser_main import ClParser
# from env.equation_net.net.eq_net import NetEditor

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('tests.tester.tests_common')

# if using directly uncoment that:
# create logger
import logging

log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('clause')
logger.setLevel(level=log_level)

logger.debug('sys.path[0]')
logger.debug(sys.path[0])


class Clause():

    def __init__(self, sent, db=None, trace=0):

        '''db had been initiated with path and ``load_all_tables``
        had been used (see also ``parser_main.EqParser.__init__``
        where it used)'''

        if db is not None:
            self.db = db
        else:
            from gui.web.model.model_main import TokenizerDB
            self.db = TokenizerDB()
            # self.path_db = "env/clause/data/terms/input/demo_dialect.db"
            self.db.change_dialect_db("cs")

        self.parser = ClParser(self)
        
        # remove spaces:
        self.sent = sent.replace(' ', "")

        self.operator_tree = None

        # for debugging:
        self.trace = trace

    def show_original(self):
        print(self.sent)
        # print(self.tree.flatten("original"))
    
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

    sent = "abelian(G) \\and subgroup(H, G,) => abelian(H)"
    print("\noriginal:")
    print(sent)
    
    eq = Clause(sent)
    eq.parser.parse()
    
    print("\nresult:")
    print(eq.show_net_json_original())

