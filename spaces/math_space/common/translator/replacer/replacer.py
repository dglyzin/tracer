import abc


class Params():
    pass


class Gen():
    metaclass = abc.ABCMeta

    '''Base class for tree's nodes translator
    When it calling ``self.__call__`` for some node it choice
    node type (bracket or not) and add output
    to that according to terms generators id.
    For that method ``self.tranlate`` and ``self.translate_brackets``
    must exist. They default value implemented here but if more
    behavior is needed they must be owerided then.
    This methods should add some output to node. For that
    ``self.set_output``, ``self.set_output_out``, ``self.set_output_data``
    must be implemented (distination to set data
    ex: ``node.output.cpp.out``)

    When it initiated (``self.__init__``) it set ``self.global_params``
    and terms generator from
    ``self.get_terms_gen_cls`` and ``self.get_terms_br_gen_cls``
    so this method must be implimentend.

    For extract term id for not brackets term ``self.get_term_id``
    method default exist but if more behavior needed it must be owerided.
    For bracket term id see replacer_brackets.

    This class is suppose to be implimentend for each output
    type (cpp, sympy,...)
    '''

    def __init__(self):

        '''set up terms generator from
        ``self.get_terms_gen_cls`` and ``self.get_terms_br_gen_cls``
        that must be impolimented.'''

        # some global data to extract from all
        # nodes in tree:
        self.global_params = Params()

        # extract terms generators classes:
        terms_gens_cls = self.get_terms_gen_cls()
        terms_br_gens_cls = self.get_terms_br_gen_cls()

        if terms_gens_cls is None:
            return
        if terms_br_gens_cls is None:
            return

        # terms generators for simple terms:
        self.terms_gens = {}

        for gen in terms_gens_cls:
            term = gen(self)
            self.terms_gens[term.id] = term

        # for brackets:
        self.terms_br_gens = terms_br_gens_cls(self)
            
    @abc.abstractmethod
    def get_terms_gen_cls(self):
        raise(BaseException(('get_terms_gen_cls method of Gen class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def get_terms_br_gen_cls(self):
        raise(BaseException(('get_terms_br_gen_cls method of Gen class'
                             + ' must be implemented')))

    def __call__(self, node):

        '''Check if ``node.name`` is Word and if it is, call
        tranlate method for simple nodes,
        translate_brackets for brackets (node.name == 'br').

        Input:
           nodes must be of type Node
        Return:
           add node.output data'''

        node_type = self.get_node_type(node)

        if(node_type == 'br'):  # type(node.name) == Word and
            # for branches (a+...)^3 or sin(a+...):
            self.translate_brackets(node)
            # leftb = node.children[0]
            # rightb = node.children[-1]
            # leftb, rightb = self.translate_brackets(leftb, rightb)
            # X = (leftb, rightb)
        elif type(node_type) == str:
            # if node.name is not in lexem:
            pass
            # X = node
        elif(node_type != 'br'):  # type(node.name) == Word and
            # if node.name is type(Word)
            # it can be branch too
            # (in case of one argument
            # like (a)^3 or sin(a)):
            self.translate(node)
            # X = self.add_out_to(node)

        # return(X)
 
    def translate_brackets(self, node):
        
        self.get_args_br(node)
        self.init_output([node])
        
        # add out to node:
        self.terms_br_gens(node)

    def translate(self, node):

        '''
        Add out to node.
        Extract data from pattern (if any exist for such pattern)
        and add it to node.
        Specific to cpp is:
           node.cpp out
           term_id location (node.name.lex[-1])
        
        Output:
        node:
           (node.cpp.out, node.cpp.global_data)

        Input:
        node:
           node.name.lex = ['D[U,{x,2}]', <_sre.SRE_Match object>,
                            'diff_pattern']
        '''
        self.get_args(node)
        self.init_output([node])

        # find generator for node:
        term_id = self.get_term_id(node)
        if term_id is None or term_id not in self.terms_gens:
            term_id = 'default'

        # add out:
        self.terms_gens[term_id](node)

    def get_successors(self, node):
        successors = node.children
        return(successors)

    def get_node(self, node):
        return(node)

    def get_node_type(self, node):
        return(node.name)

    def get_args(self, node):

        '''Extract common args from node'''

        try:
            node.args
        except AttributeError:
            node.args = {}
            node.args['id'] = {}
            node.args['id']['term_id'] = self.get_term_id(node)
            node.args['id']['name'] = self.get_term_value(node)
            
    def get_args_br(self, node_br):
    
        '''Extract common args from bracket node'''
   
        left_node = node_br[0]
        right_node = node_br[-1]

        self.get_args(left_node)
        self.get_args(right_node)

    @abc.abstractmethod
    def init_output(self, nodes):

        '''Add init out obj to each node in nodes'''

        raise(BaseException(('init_output method of Gen class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def set_output_out(self, node, value):

        '''add value to out object of node.
        out object added with init_output'''

        raise(BaseException(('set_output method of Gen class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def set_output_data(self, node, key, value):

        '''append value to global_data of node.
        global_data added with init_output'''
        
        raise(BaseException(('set_output_data method of Gen class'
                             + ' must be implemented')))

    @abc.abstractmethod
    def get_params_field_name(self):

        '''name of field for implemenation params in
        node global_data'''
        
        raise(BaseException(('get_params_field_name method of Gen class'
                             + ' must be implemented')))

    def get_term_id(self, node):

        '''Get term id from node'''

        return(node.name.lex[-1])

    def get_term_value(self, node):
        return(node.name.lex[0])

    def get_term_pattern(self, node):
        return(node.name.lex[1])
    
    # FOR flatten:
    def get_extractor(self, key="original"):
        if key == "original":
            return(self.extractor_original)

    def extractor_original(self, node):
        
        try:
            out = self.get_term_value(node)
        except:
            out = self.get_node_type(node)
        return(out)
    # END FOR
