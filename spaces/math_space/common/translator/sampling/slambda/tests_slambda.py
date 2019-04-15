# parser$ python3 -m translator.sampling.slambda.tests_slambda

from copy import deepcopy

from translator.sampling.slambda.tree_editor import test_set_slambda
# from translator.tree.tests_map import test as test_map
# from translator.sampling.slambda.tree_editor import TreeEditor

from translator.sampling.slambda.data.stable import stable
from translator.sampling.slambda.data.stable import sign_module_name
import translator.sampling.slambda.data.gens.algebra.groups as groups


def sampling_of_single_node(node, ventry, stable):
    
    '''
    If node has no "mem_sign" key, it will
    be added (for memorization of generated signs).

    If ventry is not complite with node name
    or args, it will be (with None values).

    Return either list of successful samples (entries)
    (for entry sign) or failure (None).

    For ``rand`` signature type failure means no results
    after N samples.

    If failure, ``failure_statuses`` for node["name"]
    will be added as description of cause.'''

    node_data = node["data"]["slambda"]

    if node_data["stname"] not in stable:
        print("no generator for: ", node_data["stname"])

    # if node not exist yet in vtentry,
    # add it:
    if node_data["vtname"] not in ventry:
        ventry[node_data["vtname"]] = None

    # if node args not exist in ventry:
    # add it:
    for arg in node_data["args"]:
        if arg not in ventry:
            ventry[arg] = None

    # collect node.sign to work with:
    # (ex: for node["args"] = [X, Y] and node["name"] = f
    #  and sign [X, Y, Out], collect [None, 1, True],
    #  where values taken from ventry):
    target_attrs = [arg for arg in node_data["args"]]
    target_sign_val = [ventry[arg]
                       for arg in node_data["args"]]
    target_sign = [True if ventry[arg] is not None
                   else False for arg in node_data["args"]]
    '''
    target_attrs.append(node_data["vtname"])
    target_sign_val.append(ventry[node_data["vtname"]])
    target_sign.append(True
                       if (ventry[node_data["vtname"]]
                           is not None)
                       else False)
    '''
    target_attrs = tuple(target_attrs)
    target_sign_val = tuple(target_sign_val)
    target_sign = tuple(target_sign)
    print("target_attrs:")
    print(target_attrs)
    print("target_sign_val:")
    print(target_sign_val)
    print("target_sign:")
    print(target_sign)

    # memorization:
    if "mem_sign" not in node_data:
        node_data["mem_sign"] = {}

    # if there is previus results
    # use it:
    if target_sign_val in node_data["mem_sign"]:
        mem_sign = node_data["mem_sign"][target_sign_val]

        if mem_sign is None:
            msg = "failure found in mem_sign"
            return((None, msg))
        else:
            n_entries = [create_new_entry(node_data, target_attrs,
                                          sign_value, ventry)
                         for sign_value in node_data["mem_sign"][target_sign_val]]
            return((n_entries, None))

    # if there is none, generate new:

    # generate new samples with use
    # of sign generators (for target_sign_val):
    if target_sign not in stable[node_data["stname"]]:
        msg = ("no such signature for: " + node_data["stname"]
               + " " + str(target_sign))
        print(msg)
        print("available signs for node ", node_data["stname"])
        print(stable[node_data["stname"]])
        # ventry["failure_statuses"][node_data["name"]] = msg
        return((None, msg))
    else:
        target_sign_stdata = stable[node_data["stname"]][target_sign]

        # get generator from:
        # (like groups.sub_X_y_out)
        gen = eval(sign_module_name+target_sign_stdata["name"])
        _type = target_sign_stdata["type"]
        
        if _type == "det":
            # if result is determent:
            res = gen(target_sign_val)
            if res is not None:
                n_entry = create_new_entry(node_data, target_attrs,
                                           res, ventry)
                node_data["mem_sign"][target_sign_val] = [res]
                return(([n_entry], None))
            else:
                # failure:
                node_data["mem_sign"][target_sign_val] = None
                msg = ("wrong value,"
                       + " ")
                # ventry["failure_statuses"][node_data["name"]] = msg
                return((None, msg))

        elif _type == "rand":
            # if result is random:
            res_success = []
            previus_states = []
            N = target_sign_stdata["count_of_samples"]
            for step in range(N):
                res, previus_states = gen(target_sign_val, previus_states)
                if previus_states is None:
                    # states empty:
                    break
                if res is not None:
                    res_success.append(res)

            # if there is some results:
            if len(res_success) > 0:
                n_entries = [create_new_entry(node_data, target_attrs,
                                              sign_value, ventry)
                             for sign_value in res_success]
                node_data["mem_sign"][target_sign_val] = res_success
                return((n_entries, None))
            else:
                # failure:
                node_data["mem_sign"][target_sign_val] = None
                msg = ("rand count achived,"
                       + " no results")
                # ventry["failure_statuses"][node_data["name"]] = msg
                return((None, msg))


def create_new_entry(node_data, sign, sign_values, parent_entry):
    n_entry = deepcopy(parent_entry)
    for idx, attr in enumerate(sign):
        n_entry[attr] = sign_values[idx]

    # if ventry has no attribute checked_nodes
    # add it:
    if "checked_nodes" not in n_entry:
        n_entry["checked_nodes"] = [node_data["vtname"]]
    else:
        n_entry["checked_nodes"].append(node_data["vtname"])

    n_entry["parent_idd"] = parent_entry["idd"]
    n_entry["idd"] = str((eval(parent_entry["idd"])
                          + [parent_entry["successors_count"]]))
    parent_entry["successors_count"] += 1
    n_entry["successors_count"] = 0
    return(n_entry)


if __name__ == "__main__":

    # target proposal:
    # "abelian(G) \\and subgroup(H, G,) => abelian(H)"
    # set slambda data to each node:
    net, nodes = test_set_slambda(22)

    # take idd of subgroup and abelian terms:
    subgroup_idd = [idd for idd in nodes
                    if net.node[idd]["data"]["slambda"]["stname"] == "subgroup"][0]
    abelian_idd = [idd for idd in nodes
                   if net.node[idd]["data"]["slambda"]["stname"] == "abelian"][0]

    idds = [("subgroup", subgroup_idd),
            ("abelian", abelian_idd)]

    # create value table:
    test_vtable = [

        # both H and G are given
        # => just check target proposal:
        {"H": ("(2,4)(3,5)",),
         "G": ("(2,4)(3,5)", "(2,5,4,3)"),
         "idd": str(["s"]), "successors_count": 0},
        
        # G is not given
        # => must be generating during sampling
        {"H": ("(2,3)(4,5)",),
         subgroup_idd: True, abelian_idd: True,
         "idd": str(["s"]), "successors_count": 0},
        
        # H is not ginven
        # => must be generating during sampling
        {"G": ("(1,2)(3,5)", "(1,5,2,3)"),
         subgroup_idd: True, abelian_idd: True,
         "idd": str(["s"]), "successors_count": 0},
        {"G": ("(1,4)(2,3)", "(1,3)(2,4)"),
         abelian_idd: True, subgroup_idd: True,
         "idd": str(["s"]), "successors_count": 0}]
    
    print("subgroup node:\n")
    print(net.node[subgroup_idd])
    print("\nabelian node:\n")
    print(net.node[abelian_idd])

    print("\n========= Tests for each entry in vtable ===========\n")
    for entry in test_vtable:
        # FOR print:
        print("\n+++++++++++++ for entry: +++++++++++++")
        print(entry)

        for (pred_name, pred_idd) in idds:
            print("\n------------for " + pred_name + ": ",
                  pred_idd, "------------")
            pred_node_data = net.node[pred_idd]["data"]["slambda"]

            # print node args:
            print("from node:")
            print(pred_name + "(", str(pred_node_data["args"][:-1]),
                  ")\n")

            # print node args entry values:
            pred_args = [entry[arg] if (arg in entry
                                        and entry[arg] is not None)
                         else arg
                         for arg in pred_node_data["args"][:-1]]
            pred_out = "None"
            if pred_idd in entry:
                pred_out = entry[pred_idd]
            print("from vtentry:")
            print(pred_name + "(", str(pred_args), ") = ",
                  pred_out, "\n")
            # print(net.node[subgroup_idd]["data"]["slambda"])
            # END FOR

            out, msg = sampling_of_single_node(net.node[pred_idd],
                                               entry, stable)
            print("out:")
            print(out)
            if out is not None:
                print(len(out))
            print("msg:")
            print(msg)

    print("\ntest_vtable:")
    for entry in test_vtable:
        print(entry, "\n")
