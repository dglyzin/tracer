# parser$ python3 -m translator.sampling.slambda.tests_tree_editor
from translator.sampling.slambda.tree_editor import TreeEditor
from translator.sampling.slambda.data.stable import stable
from translator.tree.tests_map import test


def test_set_slambda(_id):

    D = test("cs", _id)

    tree_editor = TreeEditor()
    tree_editor.set_mid_terms(["clause_where", "clause_for", "clause_into",
                               "def_0", "in_0",
                               "if", "if_only", "if_def",
                               "clause_or", "conj"])
    tree_editor.set_stable_names(list(stable.keys()))
    tree_editor.set_vars_terms(["set", "var"])
    
    tree_editor.set_parsed_net(D)
    
    slambda_nodes_idds = []
    
    # add slambda key for each node in D
    # which name exist in stable:
    for node_idd in D.node:
        slambda = tree_editor(node_idd)
        if slambda is not None:
            if D.node[node_idd]["name"] == "br":
                left_node_idd = tree_editor.get_successors(node_idd)[0]
                slambda_nodes_idds.append(left_node_idd)
            else:
                slambda_nodes_idds.append(node_idd)
    return((D, slambda_nodes_idds))


if __name__ == "__main__":

    # "abelian(G) \\and subgroup(H, G,) => abelian(H)"
    net, nodes = test_set_slambda(22)
    print("\nnodes with slambda values:")
    for idd in nodes:
        print(idd)
    print()
