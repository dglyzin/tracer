# parser$ python3 -m translator.tree.tests_map
import translator.grammar.tests_cyk as ts
import translator.tree.maps as ms
import math
import networkx as nx
from networkx.readwrite import json_graph


def test(dialect):

    if dialect == "cs":
        tokenizer = ts.make_tokenizer(ts.cs)
        ot = ts.test_one(tokenizer, ts.tests_dict_cs,
                         "cs", _id=19, verbose=True)
    
    elif dialect == "eqs":
        tokenizer = ts.make_tokenizer(ts.eqs)
        ot = ts.test_one(tokenizer, ts.tests_dict_eqs,
                         "eqs", _id=11, verbose=True)

    ms.map_tree_id(ot)
    D = nx.DiGraph()
    ms.map_tree_to_net(D, ot)
    # print("D.nodes(data=True):")
    # print(D.nodes(data=True))
    print("\nD.nodes()")
    print(D.nodes())

    print("\nD.edges()")
    print(D.edges())
    
    D = ms.set_max_height(D)
    D = ms.set_max_width(D)
    D = ms.set_position(D, [["['s']"]], {"x": 400, "y": 100},
                        lambda dx, level: 10*level,
                        lambda w, level: w**2+level)
    # lambda idd: 1200/math.log2(len(idd))
        
    cy_out = ms.map_net_nx_to_cy(D)
    print("map_net_id:")
    print(cy_out)
    
    # work
    print("node_link_data:")
    # print(json_graph.node_link_data(D))

    print("list(D)")
    print(list(D))

    # print("node_link_graph:")
    # print(json_graph.node_link_graph(D))

    # work:
    # print("adjacency_data:")
    # print(json_graph.adjacency_data(D))

    # print("adjacency_graph:")
    # print(json_graph.adjacency_graph(D))

    # work:
    # print("tree_data:")
    # print(json_graph.tree_data(D, "['s']"))

    # print("tree_graph:")
    # print(json_graph.tree_graph(D))
    
    return(D)


if __name__ == "__main__":
    
    # test("cs")
    test("eqs")
