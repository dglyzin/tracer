from translator.tokenizer.patterns.patterns_list.tests.dialects import cs
from translator.grammar.grammars import get_fmw
from translator.main.parser_general import ParserGeneral

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('clause.cl_parser')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('eq_parser')
logger.setLevel(level=log_level)
'''


class ClParser():

    def __init__(self, net):
        self.net = net

        self.grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                        "clause_into"],
                                       "def_0", "in_0",
                                       ["if", "if_only", "if_def"],
                                       "clause_or", "conj"])
        self.dialects_patterns = {}
        
        if self.net.db is None:
            print("patterns from tests.dialects.eqs used")
            self.dialects_patterns["hol"] = cs
        else:
            print("patterns from db used")
            dialect = self.net.db.get_entries_to_list()
            self.dialects_patterns["hol"] = dialect

        self.mid_names = {"ops": ["clause_where", "clause_for",
                                  "clause_into",
                                  "def_0", "in_0",
                                  "if", "if_only", "if_def",
                                  "clause_or", "conj"]}
        self.parsers = {}
        self.parsers["hol"] = ParserGeneral(self.dialects_patterns["hol"],
                                            self.grammar_fmw, self.mid_names)
        
        self.parser_current = "hol"

    def show_patterns(self):

        '''call ``tokenizer.show_patterns`` method'''

        self.parsers[self.parser_current].show_patterns()

    def parse(self):
        
        sent_list = [self.net.sent]

        self.parsers[self.parser_current].parse(sent_list)

        self.net.lex_out = self.parsers[self.parser_current].lex_out
        self.net.cyk_out = self.parsers[self.parser_current].cyk_out
        self.net.tree_out = self.parsers[self.parser_current].tree_out
        self.net.net_out = self.parsers[self.parser_current].net_out
        self.net.json_out = self.parsers[self.parser_current].json_out
        # set net for replacer:
        # self.net.replacer.cpp.gen.set_parsed_net(self.net.net_out)

        # print("\nparser.net_out:")
        # print(self.net.net_out.node)

        # print("\nparser.json_out:")
        # print(self.net.json_out)

        
