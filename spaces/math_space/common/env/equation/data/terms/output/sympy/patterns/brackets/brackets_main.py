from translator.replacer.replacer_brackets import GenBrackets

from env.equation.data.terms.output.sympy.patterns.brackets.func import Func
from env.equation.data.terms.output.sympy.patterns.brackets.idx import Idx

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_sympy.brackets_main')

# if using directly uncoment that:

'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('cpp_net')
logger.setLevel(level=log_level)
'''

terms_br_gens = [Func, Idx]


class Out():
    pass


class BracketsNet(GenBrackets):
    
    '''Class for all brackets terms.
    Terms for brackets replacement will be
    in self[]'''

    def get_terms_gen_cls(self):
        return(terms_br_gens)
