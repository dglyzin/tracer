def subs(net, net_vars, **kargs):

    for var in kargs:
        
        indexs = is_entry_index_exist(var, net_vars,
                                      test=lambda var, arg: var == arg["id"]["var"])
        if indexs is not None:
            for index in indexs:
                net_vars[index]["id"]["val"] = kargs[var]

                # set up var for all nodes:
                for node_name in net_vars[index]["nodes"]:
                    net.node[node_name]["data"]["vars"]["self"]["val"] = kargs[var]
    return(net_vars)


def get_args(node_name, net, vars_extractor):

    '''set vars for node that is it's vars and vars of
    it's args (if any exist)

    Inputs:

    - ``terms_vars`` -- dict with terms and they possible
    values.

    - ``terms_spec`` -- list with terms special, that
    never have values.

    Outputs:

    Return vars dict for node_name
    Each key is pair (var, value) (can be None).

    (ex: {(f, None): [['s', 1]]} for f() in second
     successor (arg) of node with id ['s'])

    (ex: {(None, sin): [['s', 0]]} for sin() in first
     successor (arg) of same node)

    Each "vars" key to each node["data"] will be added:
    {"self": self_vars, "args": args_vars}
    '''
    # successors, self_var = term_list[term_id].get_node_args(node_name, net)

    node = net.node[node_name]
    terms_spec = vars_extractor.get_terms_spec()
    
    node_successors = []
    var_or_val = None
    target_node_name = None

    if node["name"] == "br":
        
        node_successors_ids = net.successors(node_name)
        node_successors_ids.sort(key=lambda elm: eval(elm)[-1])

        left_node_name = node_successors_ids[0]
        left_node = net.node[left_node_name]

        # find args names:
        args_node_names = net.successors(node_successors_ids[1])
        args_node_names.sort(key=lambda elm: eval(elm)[-1])

        right_node_name = node_successors_ids[-1]
        # print("left_node:")
        # print(left_node)

        if ("data" in left_node) and (left_node["data"] is not None):
            term_name = left_node["data"]["term_name"]
        
            if term_name not in terms_spec:

                # if node alredy have vars:
                if "vars" not in left_node["data"]:

                    target_node_name = left_node_name
                    lex_value = left_node["data"]["lex_value"]
                    var_or_val = vars_extractor.map_ltv(term_name, lex_value)

        node_successors = args_node_names

    elif node["name"] == "a":
        
        term_name = node["data"]["term_name"]
        
        if term_name not in terms_spec:
            
            # if node alredy have vars:
            if "vars" not in node["data"]:
                target_node_name = node_name
                lex_value = node["data"]["lex_value"]
                var_or_val = vars_extractor.map_ltv(term_name, lex_value)
            
        # a term has no successors:
        # node_successors = net.successors(node_name)
        # node_successors.sort(key=lambda elm: eval(elm)[-1])

    else:
        # middle term:
        node_successors = net.successors(node_name)
        node_successors.sort(key=lambda elm: eval(elm)[-1])

    self_var = None
    if var_or_val is not None:
        
        # check if var_or_val is var:
        if vars_extractor.is_var_or_val(term_name, var_or_val):
            self_var_id = {"term_id": term_name, "var": var_or_val,
                           "val": None}
        else:
            # is val:
            self_var_id = {"term_id": term_name, "var": None,
                           "val": var_or_val}
        self_var = {"id": self_var_id,
                    "nodes": [node_name]}

    # vars from node.args:
    args_vars = []
    for succ in node_successors:
        arg = get_args(succ, net, vars_extractor)
        args_vars.append(arg)

    # print("node:")
    # print(net.node[node_name])

    # each node will be knew its vars:
    # (if it has one)
    if target_node_name is not None:
        net.node[target_node_name]["data"]["vars"] = {"self": self_var,
                                                      "args": args_vars}

    # FOR output vars:
    out_vars = []

    # print("args_vars")
    # print(args_vars)

    # check and add args_vars
    for arg_vars in args_vars:
        for arg_var_entry in arg_vars:
            indexs = is_entry_index_exist(arg_var_entry, out_vars)
            if indexs is not None:
                for index in indexs:
                    out_vars[index]['nodes'].extend(arg_var_entry["nodes"])
            else:
                out_vars.append({'id': arg_var_entry['id'],
                                 'nodes': arg_var_entry["nodes"]})

    # check and add self_vars
    if self_var is not None:
        indexs = is_entry_index_exist(self_var, out_vars)
        if indexs is not None:
            for index in indexs:
                out_vars[index]["nodes"].extend(self_var["nodes"])
        else:
            out_vars.append(self_var)
    # END FOR

    return(out_vars)


def is_entry_index_exist(entry, in_list,
                         test=lambda entry, arg: entry['id'] == arg['id']):
    indexs_exist = [index for (index, arg) in enumerate(in_list)
                    if test(entry, arg)]
    if len(indexs_exist) > 0:
        return(indexs_exist)
    else:
        return(None)
