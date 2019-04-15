# python3 -m translator.sampling.slambda.tests_slambda_synch
import translator.sampling.slambda.tests_slambda as ts
from translator.sampling.slambda.data.stable import stable_fixed

from copy import deepcopy


def init_ventry(ventry, net, nodes_names):

    if "checked_nodes" not in ventry:
        ventry["checked_nodes"] = []
    
    if "failure_statuses" not in ventry:
        ventry["failure_statuses"] = {}
    
    if "idd" not in ventry:
        ventry["idd"] = str(["se"])

    if "parent_idd" not in ventry:
        ventry["parent_idd"] = None

    if "successors_count" not in ventry:
        ventry["successors_count"] = 0

    for node_name in nodes_names:

        node_sdata = get_node_slambda_data(net.node[node_name])

        # if node has no args (like H, G):
        if "args" not in node_sdata:
            continue

        # if node not exist yet in vtentry,
        # add it:
        if node_name not in ventry:
            ventry[node_name] = None

        # if node always has fixed value
        # (for self and for it's args):
        if node_sdata["stname"] in stable_fixed:
            
            # for all args including self:
            for idx, arg in enumerate(node_sdata["args"]):
                ventry[arg] = stable_fixed[node_sdata["stname"]][idx]

                # including node to checked:
                if node_sdata["vtname"] not in ventry["checked_nodes"]:
                    ventry["checked_nodes"].append(node_sdata["vtname"])
    return(ventry)


def test_synch(_id=0):

    print("target proposal:")
    print("abelian(G) \\and subgroup(H, G,) => abelian(H)")

    # set slambda data to each node:
    net, nodes_idds = ts.test_set_slambda(22)

    nodes = dict([(node_idd, net.node[node_idd])
                  for node_idd in nodes_idds])

    # take idd of subgroup and abelian terms:
    subgroup_idd = [idd for idd in nodes
                    if net.node[idd]["data"]["slambda"]["stname"] == "subgroup"][0]
    abelian_idd = [idd for idd in nodes
                   if net.node[idd]["data"]["slambda"]["stname"] == "abelian"][0]
   
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

    print("input test data:")
    print(test_ventry)

    init_ventry(test_ventry, net, nodes)

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
    results = synch(nodes, test_ventry, [], max_steps=10)
    successes, failures, state = results

    if len(successes) > 0:
        print("synch success result:")
        for success in successes:
            print(success)
            print()
    else:
        print("no successful results")
        print("last state:")
        for entry in state:
            print(entry)
            print()
    return(results)


def get_node_slambda_data(node):
    return(node["data"]["slambda"])


def synch(nodes, initial_ventry, previus_state, steps=0, max_steps=10):
    
    '''Init call must be:
    synch(nodes, initial_ventry, [])'''

    if steps > max_steps:
        print("steps over")
        return((None, None, previus_state))

    if previus_state == []:
        # init:
        state0 = {initial_ventry["idd"]: initial_ventry}
    else:
        state0 = previus_state

    # FOR collecting data:
    nodes_entries = {}
    for node_idd in nodes:
        node = nodes[node_idd]
        node_sdata = get_node_slambda_data(node)

        # if node like G, H:
        if "args" not in node_sdata:
            continue

        if node_idd not in nodes_entries:
            nodes_entries[node_idd] = []

        for ventry_name in state0:
            ventry = state0[ventry_name]
            # print("\nventry:")
            # print(ventry)
            if node_sdata["vtname"] in ventry["checked_nodes"]:
                # if alredy checked with this node:
                continue
            else:
                # copy data for process:
                nodes_entries[node_idd].append(ventry)
                # nodes_entries[node_idd].append(deepcopy(ventry))
    # END FOR

    # FOR synch data:
    state1 = {}
    successes = []
    failures = []
    for node_idd in nodes_entries:
        node = nodes[node_idd]
        node_sdata = get_node_slambda_data(node)

        for entry in nodes_entries[node_idd]:
            succ_entries, msg = ts.sampling_of_single_node(node, entry,
                                                           ts.stable)
            entry_idd = entry["idd"]
            if succ_entries is None:
                # if parent_idd is not None:
                # add failure reason to parent:
                state0[entry_idd]["failure_statuses"][node_sdata["vtname"]] = msg
            else:
                for succ_entry in succ_entries:
                    if all_nodes_checked(nodes, succ_entry):
                        if all_nodes_values_exist(nodes, succ_entry):
                            successes.append(succ_entry)
                        else:
                            failures.append(succ_entry)
                    else:
                        # add new entries to new state:
                        state1[succ_entry["idd"]] = succ_entry
                        '''
                        if succ_entry["idd"] not in state1:
                            state1[succ_entry["idd"]] = [succ_entry]
                        else:
                            state1[succ_entry["idd"]].append(succ_entry)
                        '''

            # if parent_idd is not None:
    
            # add checked_node to parent:
            # state0[entry_idd]["checked_nodes"].append(node_sdata["vtname"])
    # END FOR

    print("steps:")
    print(steps)
    print("\nstate0:")
    for idd in state0:
        print(idd)
        print(state0[idd])
    print()

    print("\nstate1:")
    for idd in state1:
        print(idd)
        print(state1[idd])
    print()

    if state1 == {} or len(successes) > 0:
        return(successes, failures, state1)
    else:
        steps += 1
        return(synch(nodes, [], state1,
                     steps=steps, max_steps=max_steps))


def all_nodes_checked(nodes, entry):
    
    pred_nodes_names = set([name for name in nodes
                            if "args" in get_node_slambda_data(nodes[name])])
    # nodes_names = set(nodes.keys())
    entry_checked_nodes_names = set(entry["checked_nodes"])
    if len(pred_nodes_names.difference(entry_checked_nodes_names)) == 0:
        return(True)
    else:
        return(False)


def all_nodes_values_exist(nodes, entry):

    pred_nodes_names = set([name for name in nodes
                            if "args" in get_node_slambda_data(nodes[name])])
    # nodes_names = set(nodes.keys())

    for node_name in pred_nodes_names:
        if entry[node_name] is None:
            return(False)
    return(True)


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
    test_synch(3)
