import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
print(env_dir)
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
    
    def __init__(self, sent, trace=0):
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

    def show_tree_original(self):
        print(self.net_out.node)
    
    
