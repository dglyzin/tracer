import abc


class Out():
    pass


class GenBrackets(dict):
    metaclass = abc.ABCMeta

    '''Class for all brackets terms.
    Terms for brackets replacement will be
    in self[]'''

    def __init__(self, net):

        # extract terms generators classes:
        terms_gens_cls = self.get_terms_gen_cls()
        self.net = net

        for gen in terms_gens_cls:
            term = gen(self)
            self[term.id] = term

    @abc.abstractmethod
    def get_terms_gen_cls(self):
        raise(BaseException(('get_terms_gen_cls method of GenBrackets class'
                             + ' must be implemented')))

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
    
    def get_term_br_id(self, left_node, right_node):

        '''Default. Oweride if needed'''

        term_id = 'l:'+left_node.name+'|r:'+right_node.name
        return(term_id)
