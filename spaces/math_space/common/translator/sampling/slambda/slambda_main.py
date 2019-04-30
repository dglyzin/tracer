from translator.sampling.slambda.tree_editor import TreeEditor
from translator.sampling.slambda.slambda_synch import ValTableSynch
import translator.tree.maps as ms

from functools import reduce


class ValTableSampling():

    '''Generate proposal's (parsed_net) missing vars data
    (init_ventry, vars_terms) with use of value table sampling.

    Inputs:

    - ``parsed_net`` -- proposal parsed net (see parser_general).
    
    - ``init_ventry`` -- entry with part of proposal data
    (from vars_terms or predicate's) whose other part will be
    generated here with sampling.
    (ex: for abelian(X, S_{3}) X will be missed in init_ventry
    and will be generated).
 
    - ``stable`` -- generators of each term
    (see sampling.slambda.data.stable).
    
    - ``stable_fixed`` -- terms, whose sign is always fixed
    (like mid terms)
    
    - ``vars_terms`` -- name of terms that is vars.

    Example:

    for proposal = "abelian(G)\\andsubgroup(H,G,)=>abelian(H)"
    with init vdata =
    {"G": ("(1,2)(3,5)", "(1,5,2,3)"),
     # subgroup_idd: True, abelian_idd: True,
     "idd": str(["s"]), "successors_count": 0},
    where H is not ginven
    => will be generated during sampling.

    '''

    def __init__(self, parsed_net, init_ventry,
                 stable, stable_fixed,
                 mid_terms, vars_terms):
        self.set_parsed_net(parsed_net)
        self.set_init_ventry(init_ventry)
        self.set_stable(stable, stable_fixed)
        self.set_mid_terms(mid_terms)
        self.set_vars_terms(vars_terms)
        self.successes = None

    def set_init_ventry(self, init_ventry):
        self.init_ventry = init_ventry

    def set_parsed_net(self, parsed_net):
        self.parsed_net = parsed_net

    def set_stable(self, stable, stable_fixed):
        self.stable = stable
        self.stable_fixed = stable_fixed

    def set_mid_terms(self, mid_terms):
        self.mid_terms = mid_terms

    def set_vars_terms(self, vars_terms):
        self.vars_terms = vars_terms

    def run(self, editor_out=None):
        if editor_out is None:
            nodes_net, nodes_idds = self.editor_step()
        else:
            nodes_net, nodes_idds = editor_out

        successes, vesnet = self.synch_step(nodes_net, nodes_idds)
        json_out = self.net_to_json(vesnet)
        # if successes > 0:
        self.successes = successes
        return(json_out)

    def net_to_json(self, vesnet):
        D = vesnet
        D = ms.set_max_height(D)
        D = ms.set_max_width(D)
        D = ms.set_position(D, [["['s']"]], {"x": 400, "y": 100},
                            lambda dx, level: 10*level,
                            lambda w, level: w**2+level)

        slambda_converter = ms.convert_node_data_slambda
        net_data = ms.map_net_nx_to_cy(D,
                                       node_data_converter=slambda_converter)
        self.json_out = net_data
        return(self.json_out)

    def synch_step(self, nodes_net, nodes_idds):
        
        '''sample each generator in nodes_idds for each
        collumn in init_ventry, generate result tree
        (from init_ventry to succ_ventry or fail_ventry).'''

        v_synch = ValTableSynch(nodes_net, nodes_idds,
                                self.stable, self.stable_fixed)
        v_synch.init_ventry(self.init_ventry)
        results = v_synch.synch(self.init_ventry, [])
        successes, failures, state = results
        
        return((successes, v_synch.vesnet))

    def editor_step(self):

        '''add slambda data to parsed net predicates and
        vars nodes. Return them as well.'''

        D = self.parsed_net

        tree_editor = TreeEditor()
        tree_editor.set_mid_terms(self.mid_terms)
        tree_editor.set_stable_names(list(self.stable.keys()))
        tree_editor.set_vars_terms(self.vars_terms)
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

    def get_vtable_skeleton(self, nodes_idds):
        
        '''Return hat of value table.

        - ``nodes_idds`` -- from self.editor_step'''

        nodes = self.parsed_net.node
        get_vtname = (lambda node_idd:
                      nodes[node_idd]["data"]["slambda"]["vtname"])
        get_stname = (lambda node_idd:
                      nodes[node_idd]["data"]["slambda"]["stname"])
        table_skeleton = [(node_idd,
                           get_stname(node_idd))
                          if (get_stname(node_idd) != get_vtname(node_idd))
                          else (get_stname(node_idd), get_stname(node_idd))
                          for node_idd in nodes_idds]
        # remove duplicates:
        f = lambda acc, x: acc+[x] if (x not in [y for y in acc]) else acc
        table_skeleton = list(reduce(f, table_skeleton, []))
        return(table_skeleton)
