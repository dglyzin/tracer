from translator.replacer.replacer_brackets import GenBrackets

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('replacer_brackets_patterns')

# if using directly uncoment that:

'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('cpp_net')
logger.setLevel(level=log_level)
'''

# terms_br_gens = [Func, Pow]


class Out():
    pass


class BracketsNet(GenBrackets):
    
    '''Class for all brackets terms.
    Terms for brackets replacement will be
    in self[]

    with use of patterns_editor
    '''

    def __init__(self, net, dialect_name):

        self.net = net
        self.dialect_name = dialect_name

        # extract terms generators classes:
        terms_gens_cls = self.get_terms_gen_cls()

        for term_name in terms_gens_cls:
            term = terms_gens_cls[term_name](self)
            self[term.id] = term

    def get_terms_gen_cls(self):

        '''``self.net`` and ``self.dialect_name`` must be
        ititiated first'''

        terms_br_gens = (self.net.patterns_editor
                         .load_patterns(self.dialect_name, brackets=True))
        return(terms_br_gens)
