from translator.grammar.cyk import cyk
from translator.grammar.cyk import preproc as preproc_cyk
from translator.grammar.grammars import get_fmw

from translator.tree.tree_converter import convert
# from translator.tree.nodes import NodeCommon

from translator.tokenizer.tokenizer_main import TokenizerNet

import translator.tree.maps as ms
import math
import networkx as nx


class ParserGeneral():

    def __init__(self, dialect_patterns, grammar_fmw, node_data):
        self.dialect_patterns = dialect_patterns
        self.grammar_fmw = grammar_fmw
        self.node_data = node_data

    def parse(self, sent_list):
        
        tokenizer = self.make_tokenizer()
        lex_out = self.lex_step(tokenizer, sent_list)

        # fix bug with: a |-> (a):
        if len(lex_out) == 1:
            sent_list = ["("+sent_list[0]+")"]
            print(sent_list)
            lex_out = self.lex_step(tokenizer, sent_list)
            print("lex_out bracket's bug fixed")
            print(self.lex_out)

        cyk_out = self.cyk_step(lex_out)
        tree_out = self.tree_step(cyk_out)
        net_out = self.net_step(tree_out)
        json_out = self.net_to_json(net_out)
        return(json_out)

    def net_to_json(self, net_out):
        net_data = ms.map_net_nx_to_cy(net_out)
        self.json_out = net_data
        return(self.json_out)
        
    def net_step(self, tree_out):
        ms.map_tree_id(tree_out)
        D = nx.DiGraph()
        ms.map_tree_to_net(D, tree_out)
        D = ms.set_max_height(D)
        D = ms.set_max_width(D)
        D = ms.set_position(D, [["['s']"]], {"x": 400, "y": 100},
                            lambda dx, level: 10*level,
                            lambda w, level: 70*(w)**2)
        # lambda w, level: (w+30)**2-3*level)
        # lambda dx, level: 10*level/math.log2(dx+2)
        # lambda idd: 1200/math.log2(len(idd))
        # lambda idd: ((abs(math.sin(len(idd)*math.pi/6))*math.pi/3))
    
        self.net_out = D

        # print("D.nodes(data=True):")
        # print(D.nodes(data=True))
        # print("\nD.nodes()")
        # print(D.nodes())

        # print("\nD.edges()")
        # print(D.edges())
    
        # print("map_net_id:")
        # print(ms.map_net_id(D))

        return(self.net_out)

    def tree_step(self, cyk_out):
        ot = convert(cyk_out)
        self.tree_out = ot
        return(self.tree_out)
        
    def cyk_step(self, lex_out):
        
        p, t = cyk(goal=lex_out, grammar=self.grammar_fmw,
                   node_data=self.node_data)
        self.cyk_debug = (p, t)
        self.cyk_out = t
        return(self.cyk_out)
    
    def lex_step(self, tokenizer, sent_list):
        sent_list = [sent.replace(" ", "")
                     for sent in sent_list]
        out = tokenizer.lex(sent_list)
        out = preproc_cyk(out)
        self.lex_out = out

        return(self.lex_out)

    def make_tokenizer(self):

        tokenizer = TokenizerNet()
        grammar_parts = {'a': 'a',
                         'br': {'br_left':
                                {'left': 'f',
                                 'mid': ',',
                                 'right': ')'},
                                'br_mid':
                                {'mid': 'm'},
                                'br_right':
                                {'left': '(',
                                 'mid': ',',
                                 'right': 'w'}}}
        tokenizer.set_grammar_parts(grammar_parts)
        tokenizer.load_patterns(self.dialect_patterns)

        self.tokenizer = tokenizer
        return(tokenizer)
