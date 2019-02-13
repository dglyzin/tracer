'''Convert operator tree to out

Function lex_replacer must be given by user
it transform Word's object to what it shuld be.
If no given, it transform itro original lexems.
This because of type is Word for each node.name in op_tree,
so it contain lex atribute:
   Word.lex = [lexem, re.math object]
function lambda x:x[1] return original sent.

'''
import math
import networkx as nx
from networkx.readwrite import json_graph

import logging


# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
# logger = logging.getLogger('replacer_cpp')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('maps')
logger.setLevel(level=log_level)

'''
def replace(term, lex_replacer):

    ''Replace term with lex_replacer function.
    If term is not of type Word then return term.''

    if type(term) == str:
        # if term is not in lexem:
        X = term
    else:
        # if term is type(Word)
        X = term.replace_lex(lex_replacer)
    return(X)
'''


def map_net_nx_to_cy(net):
    
    '''Transform networkx json data to cytoscape data.
    Remove unserialisable regexp data from node data.
   
    map node:

    {'name': 'f'
     'coords': {'max_height': 0,
                'max_width': 0,
                'position': {'alpha': 13.0, 'radius': 170, 'x': 372, 'y': 600},
                'width': 0},
     'data': {'lex_template': '(?P<obj>[a-z|A-Z|_|0-9]+)\\(',
              'lex_value': 'group(',
              're_res': <_sre.SRE_Match object; span=(2, 8), match='group('>,
              'term_name': 'pred',
              'term_type': 're'}}
    
    to

    {'group': 'nodes',
     'position': {'alpha': 13.0, 'x': 372, 'radius': 170, 'y': 600},
     'data': {'name': 'f',
              'idd': "['s', 1, 0, 0, 0]",
              'id': 'n17',
              'main_data': {'re_res': None, 'term_name': 'pred',
                            'lex_template': '(?P<obj>[a-z|A-Z|_|0-9]+)\\(',
                            'lex_value': 'group(', 'term_type': 're'},
              'label': 'f|pred|group('}}

    map edge: {'source': 24, 'target': 8}
    to {"group": "edges", data: {"id", id, 'source': 24, 'target': 8}}
    
    where id is id in nx_data list.
    ''' 
    
    nx_data = json_graph.node_link_data(net)
    cy_nodes = []

    for id, nx_node_entry in enumerate(nx_data["nodes"]):

        cy_node_entry = {}
        cy_node_entry["group"] = "nodes"
        
        cy_node_entry["data"] = {}
        cy_node_entry["data"]["idd"] = nx_node_entry["id"]
        cy_node_entry["data"]["id"] = "n" + str(id)
        cy_node_entry["data"]["name"] = nx_node_entry["name"]
        
        if nx_node_entry["data"] is None:
            label = ""
            cy_node_entry["data"]["main_data"] = None
        else:
            label = ("|" + nx_node_entry["data"]["term_name"]
                     + "|" + nx_node_entry["data"]["lex_value"])

            cy_node_entry["data"]["main_data"] = nx_node_entry["data"].copy()

            # remove unserialisable data:
            cy_node_entry["data"]["main_data"]["re_res"] = None

        cy_node_entry["data"]["label"] = nx_node_entry["name"] + label
      
        # set position for each node:
        cy_node_entry["position"] = nx_node_entry["coords"]["position"]
        cy_nodes.append(cy_node_entry)

    cy_edges = []
    for id, nx_edge_entry in enumerate(nx_data["links"]):
        
        cy_edge_entry = {}
        cy_edge_entry["group"] = "edges"
        
        cy_edge_entry["data"] = {}
        cy_edge_entry["data"]["id"] = "e" + str(id)
        cy_edge_entry["data"]["source"] = "n" + str(nx_edge_entry["source"])
        cy_edge_entry["data"]["target"] = "n" + str(nx_edge_entry["target"])

        cy_edges.append(cy_edge_entry)

    out_data = cy_nodes + cy_edges
    return(out_data)


def set_position(net, nodes_ids, init_position, radius_scale, alpha_scale):
    
    '''Set position in pad tree-like net,
    begining from node with id ``node_ids = [top_node_id]``
    Each node must have id like ['s', 1, 2, 3]
    and "coords" from ``set_max_width``, ``set_max_height``.
    (ex: 'coords': {'max_height': 0, 'max_width': 0, 'width': 0})
    
    Inputs:

    - ``net`` -- a tree-like net from ``map_tree_to_net`` func,
    use only after ``set_max_height``, ``set_max_width`` funcs.

    - ``nodes_ids`` -- a list of nodes_ids. For init step must
    be like [top_node_id] == ["['s']"]

    - ``init_position`` -- a dict for top_node position
    with keys "x", "y" (i.e. position of pad)
 
    - ``r_succ`` -- function for generating radius
    for next level (sibling.radius = r_succ(sibling.idd))

    - ``alpha_scale`` -- function of radius and
    it's return value must be $\in [\py/3, \py/2)$.

    Return:

    Each node in returned net will have
    
    ["coords"]["position"]{"x": int, "y": int,
                           "radius": int, "alpha": alpha}
    (ex: 'position': {'alpha': 13.0, 'radius': 170, 'x': 372, 'y': 600})

    Examples:
 
    set_position(net, [["['s']"]], {"x": 400, "y": 100},
                 lambda idd: 10/len(idd), lambda idd: len(idd)*math.pi/3)
    '''   

    if len(nodes_ids) == 0:
        return(net)

    sfirst_ids = nodes_ids.pop(0)

    # print("sfirst_ids:")
    # print(sfirst_ids)

    if len(net.predecessors(sfirst_ids[0])) == 0:
        # init top_node:

        top_node_id = sfirst_ids[0]
        top_node = net.node[top_node_id]
        top_successors = net.successors(top_node_id)
        
        top_node["coords"]["position"] = {"x": init_position["x"],
                                          "y": init_position["y"],
                                          "radius": 0}
        if len(top_successors) != 0:
            nodes_ids.append(top_successors)

        return(set_position(net, nodes_ids,
                            init_position, radius_scale, alpha_scale))

    # find parent using first from siblings:
    snodes_ids = sfirst_ids
    parent_idd = net.predecessors(snodes_ids[0])[0]
    parent = net.node[parent_idd]

    # find relative idd of siblings inside parent:
    # (with replacing ['s', 1] in ['s', 1, k] to get [k])
    ridds = [(idd, eval(idd.replace(parent_idd[:-1]+",", "["))[0])
             for idd in snodes_ids]

    # sorting siblings with use of relative idd:
    ridds.sort(key=lambda elm: elm[1])
    sni_sorted = [node_id for (node_id, _) in ridds]
    
    # find signum for each node in siblings,
    # relative to mid:
    # (ex: ['s', 0], ['s', 1], ['s', 2] |-> [-1, 0, 1])
    # (ex: ['s', 0], ['s', 1] |-> [-1, 1])
    # (ex: ['s', k] |-> [0])
    sn_count = len(sni_sorted)
    snc_half = sn_count/2
    snch_int = int(snc_half)
    signs = list(map(lambda i: (0 if (snch_int == i and snc_half != i
                                      or snch_int == 0)
                                else -1 if i < snch_int else 1),
                     range(len(sni_sorted))))
    snis_pos = [node_id for (i, node_id) in enumerate(sni_sorted)
                if signs[i] >= 0]
    snis_neg = [node_id for (i, node_id) in enumerate(sni_sorted)
                if signs[i] <= 0]
    snis_neg.reverse()

    snis_zer = [node_id for (i, node_id) in enumerate(sni_sorted)
                if signs[i] == 0]

    # print("snis_pos:")
    # print(snis_pos)
    # print("snis_neg:")
    # print(snis_neg)
    # print("snis_zer:")
    # print(snis_zer)
    
    # plus one is due to divition by zero, when
    # max_width == 0 (or there is no children):
    w_pos = [net.node[idd]["coords"]["max_width"] + 1
             for idd in snis_pos]
    w_neg = [net.node[idd]["coords"]["max_width"] + 1
             for idd in snis_neg]
    
    # print("w_pos:")
    # print(w_pos)
    # print("w_neg:")
    # print(w_neg)
    sw_pos = sum(w_pos)
    sw_neg = sum(w_neg)

    # scale = alpha_scale(sni_sorted[0])
    level = len(sni_sorted[0])

    # radius of all siblings is equal:
    # radius = radius_scale(alpha, level)
    
    dxs_pos = list(map(lambda n: (sum([alpha_scale(w, level)
                                       for w in w_pos[:n]])/sw_pos),
                       range(len(w_pos)+1)[1:]))

    dxs_neg = list(map(lambda n: (sum([alpha_scale(w, level)
                                       for w in w_neg[:n]])/sw_neg),
                       range(len(w_neg)+1)[1:]))

    # alphas_neg = list(map(lambda n: (sum(w_neg[:n])/sw_neg)*scale,
    #                       range(len(w_neg)+1)[1:]))

    x0 = parent["coords"]["position"]["x"]
    y0 = parent["coords"]["position"]["y"]
    xs_pos = [dx+x0 for dx in dxs_pos]
    # xs_pos = [radius*math.sin(alpha)+x0 for alpha in alphas_pos]

    r_pos = [radius_scale(dx, level) for dx in dxs_pos]
    ys_pos = [radius+y0 for radius in r_pos]
    # ys_pos = [radius*math.cos(alpha)+y0 for alpha in alphas_pos]

    xs_neg = [-dx+x0 for dx in dxs_neg]
    # xs_neg = [-radius*math.sin(alpha)+x0 for alpha in alphas_neg]

    r_neg = [radius_scale(dx, level) for dx in dxs_neg]
    ys_neg = [radius+y0 for radius in r_neg]
    # ys_neg = [radius*math.cos(alpha)+y0 for alpha in alphas_neg]

    for i, node_id in enumerate(snis_pos):
        net.node[node_id]["coords"]["position"] = {"x": int(xs_pos[i]),
                                                   "y": int(ys_pos[i]),
                                                   "radius": r_pos[i],
                                                   "alpha": dxs_pos[i]}
        node_successors_ids = net.successors(node_id)
        if len(node_successors_ids) > 0:
            nodes_ids.append(node_successors_ids)

    for i, node_id in enumerate(snis_neg):
        net.node[node_id]["coords"]["position"] = {"x": int(xs_neg[i]),
                                                   "y": int(ys_neg[i]),
                                                   "radius": r_neg[i],
                                                   "alpha": dxs_neg[i]}
        node_successors_ids = net.successors(node_id)
        if len(node_successors_ids) > 0:
            nodes_ids.append(node_successors_ids)

    if len(snis_zer) > 0:
        node_id = snis_zer[0]
        net.node[node_id]["coords"]["position"] = {"x": x0,
                                                   "y": radius_scale(0, level)+y0,
                                                   "radius": radius_scale(0, level),
                                                   "alpha": 0}

        node_successors_ids = net.successors(node_id)
        if len(node_successors_ids) > 0:
            nodes_ids.append(node_successors_ids)

    return(set_position(net, nodes_ids,
                        init_position, radius_scale, alpha_scale))

    
def set_max_height(net):
    
    '''Set max height for each node in tree-like net
    i.e. max deepness of each node in tree
    Each node id must be str like "['s', 1, 2, 1, 1]"
   
    Inputs:

    - ``net`` -- a net from map_tree_to_net func.

    Output:

    net, each node of which has "max_height"  key
    in node["coords"] attribute. If attribute "coords"
    does not exist, it will be created.
    
    '''
    # get all net node's idds:
    idds = net.node.keys()
    max_heights = dict([(n_idd, max([len(eval(ch_idd)) - len(eval(n_idd))
                                     for ch_idd in idds
                                     if n_idd[:-1] in ch_idd[:-1]]))
                        for n_idd in idds])

    # set attributes:
    for node_key in net.node:
        try:
            coords = net.node[node_key]["coords"]
        except KeyError:
            net.node[node_key]["coords"] = {}
            coords = net.node[node_key]["coords"]
        coords["max_height"] = max_heights[node_key]

    return(net)


def set_max_width(net):
    
    '''Set max width for each node in tree-like net_data
    i.e. max, between all node.descendants, count of children
    for each node in net's nodes.
    Also set width (count of children) for each node.

    Inputs:

    - ``net`` -- a net from map_tree_to_net func.


    Output:

    net, each node of which has "max_width" and "width" keys
    in node["coords"] attribute. If attribute "coords"
    does not exist, it will be created.
    '''
    # get all net node's idds:
    idds = net.node.keys()
    max_widths = dict([(n_idd,
                        max([len(net.edge[ch_idd])
                             for ch_idd in nx.descendants(net, n_idd)]
                            + [len(net.edge[n_idd])]))
                       for n_idd in idds])

    widths = dict([(n_idd, len(net.edge[n_idd]))
                   for n_idd in idds])

    # set attributes:
    for node_key in net.node:
        try:
            coords = net.node[node_key]["coords"]
        except KeyError:
            net.node[node_key]["coords"] = {}
            coords = net.node[node_key]["coords"]
        coords["max_width"] = max_widths[node_key]
        coords["width"] = widths[node_key]

    return(net)


def map_tree_id(tree):
    _map_tree_id([[['s'], tree]])
    return(tree)


def _map_tree_id(ids_and_nodes):

    '''Set id for each node in tree.

    id for node means list of indexes of parent.children
    list, for each parent in a path from child to top node
    (ex: node with id ['s', 0, 2, 0] means node = top_node[0][2][0]).

    id_relative for node means index of it's parent.children
    where parent is closest parent to node.
    (ex: node with id ['s', 0, 2, 0] id_relative = 0)

    First call must be:
    map_tree_id([['s'], tree])
    
    - ``ids_and_nodes`` -- list of list like [[node_id_list, node]],
    where node_id_list is list, represented node id.
    '''
    
    if len(ids_and_nodes) == 0:
        return
    else:
        first_id, first_node = ids_and_nodes.pop(0)
        first_node.id = first_id
        # first_node.id_relative = first_id[-1]
        for _id, child in enumerate(first_node.children):
            ids_and_nodes.append([first_id + [_id], child])
        return(_map_tree_id(ids_and_nodes))


def map_tree_to_net(net, tree):
    net = _map_tree_to_net([tree], net)
    return(net)


def _map_tree_to_net(nodes, net):

    '''Make net from tree (represented with nodes = [top_node])
    Each (node in nodes, node.children for each node in nodes)
    will be represented as node in net, and each node.parent
    (except None) as edge in net.

    - ``nodes`` -- [top_node] of a tree, where top_node is
    result of ``tree_converter.convert``
    - ``net`` -- networkx.DiGraph instance.'''
    
    if len(nodes) == 0:
        # finish:

        return(net)
    else:
        # main:
    
        first = nodes.pop(0)
        
        net = add_node(net, first)
        if first.parent is not None:
            net.add_edge(str(first.parent.id), str(first.id))

        for child in first.children:
            nodes.append(child)
        return(_map_tree_to_net(nodes, net))


def add_node(net, node):

    try:
        net.add_node(str(node.id), name=node.name, data=node.name.lex)
    except AttributeError:
        net.add_node(str(node.id), name=node.name, data=None)
    
    return(net)


def map_tree(tree, node_editor):

    '''Use node_raplacer for each node to add cpp
    output'''

    if len(tree.children) == 0:
        # finish:
        node_editor(tree)

        # in case node_editor added new
        # children:
        if len(tree.children) > 0:
            for child_node in tree.children:
                map_tree(child_node, node_editor)

    elif tree.name != 'br':
        # main:

        if len(tree.children) == 2:
            map_tree(tree.children[1], node_editor)
        node_editor(tree)
        map_tree(tree.children[0], node_editor)

    elif(tree.name == 'br'):
        # if brackets:
    
        # work with brackets itself:
        node_editor(tree)

        # work with brackets args:
        for _id, arg in enumerate(tree.children[1].children):
            map_tree(arg, node_editor)
    return(tree)
    

def map_tree_postproc(mapped_tree, node_editor):
    node_editor.postproc(mapped_tree)
    return(mapped_tree)
