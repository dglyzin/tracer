from translator.replacer.replacer_brackets import GenBrackets

from env.equation.data.terms.slambda.sympy.patterns.brackets.func import Func
from env.equation.data.terms.slambda.sympy.patterns.brackets.idx import Idx

terms_br_gens = [Func, Idx]


class BracketsNet(GenBrackets):
    
    '''Class for all brackets terms.
    Terms for brackets replacement will be
    in self[]'''

    def __call__(self, node_br):

        '''Find according term and add out to it'''

        left_node = node_br[0]
        right_node = node_br[-1]

        self.net.init_output((left_node, right_node))

        # try to find pattern for term:
        term_id = self.get_term_br_id(left_node, right_node)

        if term_id in self:

            # logger.debug(right_node)
            # logger.debug(left_node)

            self[term_id](node_br)

    def get_terms_gen_cls(self):
        return(terms_br_gens)
