# parser$ python3 -m translator.sampling.slambda.tests_slambda_synch
from translator.sampling.slambda.slambda_synch import ValTableSynch

import translator.sampling.slambda.tests_slambda_single as ts

import translator.tree.maps as ms

from translator.sampling.slambda.data.stable import stable_fixed
from translator.sampling.slambda.data.stable import stable


def test_synch(_id=0):

    print("target proposal:")
    print("abelian(G) \\and subgroup(H, G,) => abelian(H)")

    # set slambda data to each node:
    nodes_net, nodes_idds = ts.test_set_slambda(22)

    # nodes = dict([(node_idd, net.node[node_idd])
    #               for node_idd in nodes_idds])

    # take idd of subgroup and abelian terms:
    subgroup_idd = [idd for idd in nodes_idds
                    if nodes_net.node[idd]["data"]["slambda"]["stname"] == "subgroup"][0]
    abelian_idd = [idd for idd in nodes_idds
                   if nodes_net.node[idd]["data"]["slambda"]["stname"] == "abelian"][0]
    print("subgroup_idd:")
    print(subgroup_idd)
    print("abelian_idd:")
    print(abelian_idd)

    # create value entry:
    test_ventries = [

        # both H and G are given
        # => just check target proposal:
        {"H": ("(2,4)(3,5)",),
         "G": ("(2,4)(3,5)", "(2,5,4,3)"),
         "idd": str(["se"]), "successors_count": 0},

        # G is not given
        # => must be generating during sampling
        {"H": ("(2,3)(4,5)",),

         # subgroup_idd: True, abelian_idd: True,

         "idd": str(["s"]), "successors_count": 0},
        
        # H is not ginven
        # => must be generating during sampling
        {"G": ("(1,2)(3,5)", "(1,5,2,3)"),
         
         # subgroup_idd: True, abelian_idd: True,
         
         "idd": str(["s"]), "successors_count": 0},
        {"G": ("(1,4)(2,3)", "(1,3)(2,4)"),
         abelian_idd: True, subgroup_idd: True,
         "idd": str(["s"]), "successors_count": 0}]

    test_ventry = test_ventries[_id]

    print("\ninput test data:")
    print(test_ventry)
    v_synch = ValTableSynch(nodes_net, nodes_idds,
                            stable, stable_fixed)

    v_synch.init_ventry(test_ventry)

    '''
    print("\nnodes:")
    
    nodes_stnames = [(node_idd,
                      get_node_slambda_data(nodes[node_idd])["stname"])
                     for node_idd in nodes]
    for node_idd, node_stname in nodes_stnames:
        print(node_idd, ": ", node_stname)

    print("\nventry:")
    print(test_ventry)

    print("\nventry['checked_nodes']:")
    print(test_ventry["checked_nodes"])
    '''

    # return((test_ventry, nodes))

    # D = nx.DiGraph()

    results = v_synch.synch(test_ventry, [])
    successes, failures, state = results
 
    if len(successes) > 0:
        print("\nsynch success result:")
        for success in successes:
            print(success)
            print()
    else:
        print("\nno successful results")
        print("last state:")
        for entry in state:
            print(entry)
            print()
    return(v_synch)


if __name__ == "__main__":

    '''
    ['s', 0, 1, 0] :  H
    ['s', 1, 0, 1, 1] :  G
    ['s'] :  if
    ['s', 0, 0] :  abelian
    ['s', 1, 1, 0] :  abelian
    ['s', 1] :  conj
    ['s', 1, 0, 1, 0] :  H
    ['s', 1, 0, 0] :  subgroup
    ['s', 1, 1, 1, 0] :  G
    '''
    v_synch = test_synch(3)
    D = v_synch.vesnet
    D = ms.set_max_height(D)
    D = ms.set_max_width(D)
    D = ms.set_position(D, [["['s']"]], {"x": 400, "y": 100},
                        lambda dx, level: 10*level,
                        lambda w, level: w**2+level)
    # print("after set_position:")
    # print(D.node)
    
    cy_out = ms.map_net_nx_to_cy(D, node_data_converter=ms.convert_node_data_slambda)
    print("from cy:")
    print(cy_out)

    # out_json = json_graph.node_link_data(D)
    # print("out_json:")
    # print(out_json)
