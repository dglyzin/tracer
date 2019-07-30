from translator.replacer.replacer import Gen
from translator.replacer.replacer import Params
from translator.replacer.patterns_editor import PatternsEditor


class NetGen(Gen):

    def __init__(self):

        '''set up terms generator from
        ``self.get_terms_gen_cls`` and ``self.get_terms_br_gen_cls``
        that must be impolimented.

        with use of patterns_editor
        '''

        # some global data to extract from all
        # nodes in tree:
        self.global_params = Params()

        self.patterns_editor = PatternsEditor()

        # extract terms generators classes:
        terms_gens_cls = self.get_terms_gen_cls()
        terms_br_gens = self.get_terms_br_gen_cls()

        if terms_gens_cls is None:
            return
        if terms_br_gens is None:
            return

        # terms generators for simple terms:
        self.terms_gens = {}

        for term_name in terms_gens_cls:
            term = terms_gens_cls[term_name](self)
            self.terms_gens[term.id] = term

        # for brackets:
        self.terms_br_gens = terms_br_gens

    def __call__(self, node_idd):

        '''Call tranlate method for simple nodes,
        translate_brackets for brackets (node["name"] == 'br').

        Input:

        - ``net`` -- networkx instance

        - ``node_idd`` -- name of node in ``net``
        (like str(['s']))

        Return:
           add net.node[node_idd]["output"] data'''

        node_type = self.get_node_type(node_idd)
        if(node_type == 'br'):
            # for branches (a+...)^3 or sin(a+...):
            self.translate_brackets(node_idd)

        elif(node_type != 'br'):

            self.translate(node_idd)
 
    def translate_brackets(self, node_idd):
        
        self.init_output([node_idd])
        
        # add out to node:
        self.terms_br_gens(node_idd)

    def translate(self, node_idd):

        '''
        Add out to node.
        Extract data from pattern (if any exist for such pattern)
        and add it to node.
        
        Output:
        node:
           (node["output"]["cpp"]["out"],
            node["output"]["cpp"]["global_data"])

        Input:
        node:
           net["node_idd"]["data"] = {"lex_value": 'D[U,{x,2}]',
                                       "re_res": <_sre.SRE_Match object> or None,
                                       "term_type": "re" or "txt",
                                       "term_name": "var"}
           net["node_idd"]["name"] = grammar_name (like br, f, a, if, div)
        '''

        self.init_output([node_idd])

        # find generator for node:
        term_id = self.get_term_id(node_idd)
        if term_id is None or term_id not in self.terms_gens:
            term_id = 'default'

        # add out:
        # print("term_id")
        # print(term_id)
        self.terms_gens[term_id](node_idd)

    def get_successors(self, node_idd):
        successors = self.parsed_net.successors(node_idd)
        successors.sort(key=lambda elm: eval(elm)[-1])
        return(successors)

    def get_node(self, node_idd):
        return(self.parsed_net.node[node_idd])

    def set_parsed_net(self, net):
        self.parsed_net = net

    def set_mid_replacers(self, mid_replacers):
        '''set replacer for mid patterns
        (like "eq", "add", "sub")
        ex: {"eq": "="}'''

        self.mid_replacers = mid_replacers

    def get_term_id(self, node_idd):

        '''Get term id from node'''

        node = self.get_node(node_idd)
        term_name = None
        if node["data"] is not None or node["data"] != {}:
            if "term_name" in node["data"]:
                term_name = node["data"]["term_name"]
        return(term_name)

    def get_term_value(self, node_idd):
        node = self.get_node(node_idd)
        lex_value = None
        if node["data"] is not None or node["data"] != {}:
            if "lex_value" in node["data"]:
                lex_value = node["data"]["lex_value"]
        return(lex_value)

    def get_term_pattern(self, node_idd):
        node = self.get_node(node_idd)
        term_type = None
        if node["data"] is not None or node["data"] != {}:
            if "term_type" in node["data"]:
                if node["data"]["term_type"] == "re":
                    term_type = node["data"]["re_res"]
        return(term_type)

    def get_node_type(self, node_idd):
        node = self.get_node(node_idd)
        return(node["name"])
    
    def extractor_original(self, node):
        
        out = self.get_term_value(node)
        if out is None:
            out = self.get_node_type(node)
        return(out)
