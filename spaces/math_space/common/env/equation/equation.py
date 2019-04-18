'''
    Algorithm:

    1) lexical analysis:
          U'=c*(D[U,{x,2}+sin(x))]
       to
          a*(a+fa))
       where each a, f is type of Word, and contain original
       lexems in lex arg. (f is short for sin(,cos(,...)
    2) 1 to parse tree (by CYK):
    with grammar:
       E -> E{+-}T|T
       T->T{*/}F|T{*/}W|T{*/}V|F
       W -> (E)^
       V -> f(E)
       F->(E)|a
    (grammar_pow_f from grammars.py)
    to parse tree:
    ('E', ('T', 'T1'))
        child 0: ('T', 'a')
        child 1: ('T1', ('M', 'F'))
           child 0: ('M', '*')
              child 0: ('L', '(')
           child 1: ('F', ('L', 'F1'))
              child 1: ('F1', ('E', 'R'))
                 child 0: ('E', ('E', 'E1'))
                    child 0: ('E', 'a')
                    child 1: ('E1', ('P', 'T'))
                       child 0: ('P', '+')
                       child 1: ('T', ('LF', 'V1'))
                          child 0: ('LF', 'f')
                          child 1: ('V1', ('E', 'RF'))
                             child 0: ('E', 'a')
                             child 1: ('RF', ')')
                 child 1: ('R', ')')
    3) Convert parse tree to operator's tree
    (with convert from trees.py):
       ('M', '*')
            child 0: ('P', '+')
               child 0: ('E', 'a')
                  child 0: ('RF', ')')
                  child 1: ('LF', 'f')
               child 1: ('E', 'a')
               child 2: ('R', ')')
               child 3: ('L', '(')
            child 1: ('T', 'a')

    4) Transform operator's tree to out by replacing lexems
    with func lex_repacer (with convert from op_to_out.py):
    for lex_repacer = lambda x:x[0] result should be same as
    original sent (see op_to_out.py for more):
       
       c*(D[U,{x,2}+sin(x))]

    END OF Algorithm.

'''

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

'''
from math_space.common.env.equation.parser.parser_main import EqParser
from math_space.common.env.equation.tree.eq_tree import EqTree
from math_space.common.env.equation.replacer.repl_main import EqReplacer
from math_space.common.env.equation.args.args_main import EqArgs
from math_space.common.env.equation.slambda.slambda_main import EqSlambda
from math_space.common.env.equation.sampling.eq_sampling import EqSampling
from math_space.common.env.equation.cas.cas_main import CAS
'''

from env.equation.parser.parser_main import EqParser
from env.equation.tree.eq_tree import EqTree
from env.equation.replacer.repl_main import EqReplacer
from env.equation.args.args_main import EqArgs
from env.equation.slambda.slambda_main import EqSlambda
from env.equation.sampling.eq_sampling import EqSampling
from env.equation.cas.cas_main import CAS


import sys
import inspect
import random

import sympy

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('tests.tester.tests_common')

# if using directly uncoment that:
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)

logger.debug('sys.path[0]')
logger.debug(sys.path[0])

'''
# add import's path:
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
print(parentdir) 
'''


class Equation():

    def __init__(self, sent, trace=0):

        self.parser = EqParser(self)
        self.tree = EqTree(self)
        self.replacer = EqReplacer(self)
        self.args_editor = EqArgs(self)
        self.slambda = EqSlambda(self)
        self.sampling = EqSampling(self)
        self.cas = CAS(self)

        # Init nodes content:
        self.replacer._init_node_content()
        
        # remove spaces:
        self.sent = sent.replace(' ', "")

        # used to indicate that U->(U) for
        # single left term:
        self._left_brs_added = False

        # self.sympy_replacer = SympyGen()
        self.prefix = []
        self.operator_tree = None

        # for debugging:
        self.trace = trace
    
    def get_all_nodes(self):
        try:
            eq_tree = self.eq_tree
        except AttributeError:
            print(("has no eq_tree yiet,"
                   + " use parser.parse first"))
            eq_tree = None

        return(eq_tree)

    def show_original(self):
        print(self.tree.flatten("original"))
    
    def __repr__(self):
        out = self.sent
        return(out)

    def show_tree_original(self):
        print(self.eq_tree.show_original())
    
    
