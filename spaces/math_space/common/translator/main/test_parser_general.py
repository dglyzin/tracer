# parser$ python3 -m translator.main.test_parser_general
from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs

from translator.grammar.grammars import get_fmw
from translator.main.parser_general import ParserGeneral


def test(dialect_name, sent_list):

    # choice grammar for dialect:
    if dialect_name == "eqs":
        grammar_fmw = get_fmw()
    elif dialect_name == "cs":
        grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                   "clause_into"],
                                  "def_0", "in_0",
                                  ["if", "if_only", "if_def"],
                                  "clause_or", "conj"])
    
    # choice patterns for dialect:
    if dialect_name == "eqs":
        dialect_patterns = eqs
    elif dialect_name == "cs":
        dialect_patterns = cs

    # choice ops for dialect:
    if dialect_name == "eqs":
        node_data = {"ops": ['add', 'sub', 'mul', 'div', 'eq', ]}
        
    elif dialect_name == "cs":
        node_data = {"ops": ["clause_where", "clause_for", "clause_into",
                             "def_0", "in_0",
                             "if", "if_only", "if_def",
                             "clause_or", "conj"]}

    parser = ParserGeneral(dialect_patterns, grammar_fmw, node_data)
    parser.parse(sent_list)

    print("\nparser.net_out:")
    print(parser.net_out.node)

    print("\nparser.json_out:")
    print(parser.json_out)
        

if __name__ == "__main__":
    
    # sent_list = ["Let(G: group(G) in: abelian(G)=>commutative(G),"
    #              + " commutative(G)=>abelian(G),)"]
    # test("cs", sent_list)
    
    sent_list = ["U'=a+U+U*U*V-(b+1)*U+c*D[U,{x,2}]"]
    test("eqs", sent_list)
