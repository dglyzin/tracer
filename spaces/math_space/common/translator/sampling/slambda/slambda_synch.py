from translator.sampling.slambda.slambda_single import sampling_of_single_node

import networkx as nx

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('slambda_synch')
logger.setLevel(level=log_level)


class ValTableSynch():

    def __init__(self, nodes_net, nodes_idds,
                 stable, stable_fixed, max_steps=10):
        self.max_steps = max_steps

        self.nodes_net = nodes_net

        # value entries states net:
        self.vesnet = nx.DiGraph()

        self.nodes_idds = nodes_idds

        self.stable = stable
        self.stable_fixed = stable_fixed

    def init_ventry(self, ventry):

        if "checked_nodes" not in ventry:
            ventry["checked_nodes"] = []

        if "failure_statuses" not in ventry:
            ventry["failure_statuses"] = {}

        if "idd" not in ventry:
            ventry["idd"] = str(["s"])

        if "parent_idd" not in ventry:
            ventry["parent_idd"] = None

        if "successors_count" not in ventry:
            ventry["successors_count"] = 0

        for node_idd in self.nodes_idds:

            node_sdata = self.get_node_slambda_data(node_idd)

            # if node has no args (like H, G):
            if "args" not in node_sdata:
                continue

            # if node not exist yet in vtentry,
            # add it:
            if node_idd not in ventry:
                ventry[node_idd] = None

            # if node always has fixed value
            # (for self and for it's args):
            if node_sdata["stname"] in self.stable_fixed:

                # for all args including self:
                for idx, arg in enumerate(node_sdata["args"]):
                    ventry[arg] = self.stable_fixed[node_sdata["stname"]][idx]

                    # including node to checked:
                    if node_sdata["vtname"] not in ventry["checked_nodes"]:
                        ventry["checked_nodes"].append(node_sdata["vtname"])
        return(ventry)

    def get_node(self, node_idd):
        return(self.nodes_net.node[node_idd])

    def get_node_slambda_data(self, node_idd):
        node = self.get_node(node_idd)
        return(node["data"]["slambda"])

    def add_vnode_to_vesnet(self, ventry_idd, data):
        self.vesnet.add_node(ventry_idd, data=data)
    
    def add_vedge_to_vesnet(self, parent_idd, succ_idd):
        self.vesnet.add_edge(parent_idd, succ_idd)

    def synch(self, initial_ventry, previus_state, steps=0):

        '''
        
        Init call must be:
        synch(initial_ventry, [])'''

        if steps > self.max_steps:
            print("steps over")
            self.results = (None, None, previus_state)
            return(self.results)

        if previus_state == []:
            # init:
            state0 = {initial_ventry["idd"]: initial_ventry}
            self.add_vnode_to_vesnet(initial_ventry["idd"], initial_ventry)
        else:
            state0 = previus_state

        # FOR collecting data:
        nodes_ventries = {}
        for node_idd in self.nodes_idds:
            
            node_sdata = self.get_node_slambda_data(node_idd)

            # if node like G, H:
            if "args" not in node_sdata:
                continue

            if node_idd not in nodes_ventries:
                nodes_ventries[node_idd] = []

            for ventry_idd in state0:
                ventry = state0[ventry_idd]
                # logger.debug("\nventry:")
                # logger.debug(ventry)
                if node_sdata["vtname"] in ventry["checked_nodes"]:
                    # if alredy checked with this node:
                    continue
                else:
                    # copy data for process:
                    nodes_ventries[node_idd].append(ventry)
                    # nodes_ventries[node_idd].append(deepcopy(ventry))
        # END FOR

        # FOR synch data:
        state1 = {}
        successes = []
        failures = []
        for node_idd in nodes_ventries:
            node = self.get_node(node_idd)
            node_sdata = self.get_node_slambda_data(node_idd)

            for ventry in nodes_ventries[node_idd]:
                succ_ventries, msg = sampling_of_single_node(node, ventry,
                                                             self.stable)
                ventry_idd = ventry["idd"]
                if succ_ventries is None:
                    # if parent_idd is not None:
                    # add failure reason to parent:
                    ventry_data = state0[ventry_idd]
                    ventry_data["failure_statuses"][node_sdata["vtname"]] = msg
                else:
                    for succ_ventry in succ_ventries:
                        if self.all_nodes_checked(succ_ventry):
                            if self.all_nodes_values_exist(succ_ventry):
                                successes.append(succ_ventry)
                            else:
                                failures.append(succ_ventry)
                        else:
                            # add new entries to new state:
                            state1[succ_ventry["idd"]] = succ_ventry
                            '''
                            if succ_ventry["idd"] not in state1:
                                state1[succ_ventry["idd"]] = [succ_ventry]
                            else:
                                state1[succ_ventry["idd"]].append(succ_ventry)
                            '''

                # if parent_idd is not None:

                # add checked_node to parent:
                # state0[ventry_idd]["checked_nodes"].append(node_sdata["vtname"])
        # END FOR

        logger.debug("\n\nsteps:")
        logger.debug(steps)
        logger.debug("\n\nstate0:")
        for idd in state0:
            logger.debug("\n"+str(idd))
            logger.debug(state0[idd])

        logger.debug("\n\nstate1:")
        for idd in state1:
            self.add_vnode_to_vesnet(idd, state1[idd])
            self.add_vedge_to_vesnet(state1[idd]["parent_idd"], idd)

            logger.debug("\n"+str(idd))
            logger.debug(state1[idd])

        if len(successes) > 0:
            self.results = (successes, failures, state1)
            return(self.results)
        elif state1 == {}:
            print("exit because state1 == {}")
            self.results = (successes, failures, state1)
            return(self.results)
        else:
            steps += 1
            return(self.synch(None, state1, steps=steps))

    def all_nodes_checked(self, ventry):

        pred_nodes_names = set([idd for idd in self.nodes_idds
                                if "args" in self.get_node_slambda_data(idd)])
        # nodes_names = set(nodes.keys())
        ventry_checked_nodes_names = set(ventry["checked_nodes"])
        if len(pred_nodes_names.difference(ventry_checked_nodes_names)) == 0:
            return(True)
        else:
            return(False)

    def all_nodes_values_exist(self, ventry):

        pred_nodes_names = set([idd for idd in self.nodes_idds
                                if "args" in self.get_node_slambda_data(idd)])
        # nodes_names = set(nodes.keys())

        for node_name in pred_nodes_names:
            if ventry[node_name] is None:
                return(False)
        return(True)
