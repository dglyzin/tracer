from env.equation.data.terms.output.cpp.postproc import delay_postproc


class sysPostProc():
    '''
    Either postproc all eqs in system
    or all eqs in all systems (with postproc_delay_sys
    method).
   
    Example:(tests_sys.py):

    # create system and parse equations:
    sys_1 = System(system=[eq_1, eq_2])
    sys_2 = System(system=[eq_2, eq_3])

    # generate cpp:
    sys_1.cpp.set_default()
    sys_1.cpp.gen_cpp()
    sys_2.cpp.set_default()
    sys_2.cpp.gen_cpp()

    # collect all nodes in one place
    # (system.postproc.nodes):
    sys_1.postproc.collect_nodes()
    sys_2.postproc.collect_nodes()

    # for sinch eqs:
    sys_1.postproc.postproc_nodes()

    # for sinch eqs in all systems:
    sys_1.postproc.postproc_delay_sys([sys_2])

    '''
    def __init__(self, net, ):
        self.net = net

    def collect_nodes(self):
        
        '''Collect nodes from all equations (for postproc)
        self.net.eqs must exist so use
           sys.cpp.set_default
           sys.cpp.gen_cpp
        first
        '''

        self.nodes = [[node for node in eq.get_all_nodes()]
                      for eq in self.net.eqs]
        # self.nodes = [node for eq in self.net.eqs
        #               for node in eq.get_all_nodes()]

        self.replacers = [eq.replacer.cpp.gen for eq in self.net.eqs]
        # self.replacer = self.net.eqs[0].replacer.cpp.gen
    
    def postproc_delay_nodes(self):

        '''Postproc delays in all eqs.
        self.nodes must exist (from collect_nodes method)'''

        delay_postproc(self.replacers, self.nodes)

    def postproc_delay_sys(self, systems):

        '''postproc delays in all eqs in all systems'''

        # add self.nodes to global:
        common_nodes = self.nodes[:]
        common_replacers = self.replacers[:]

        # add other systems nodes to global:
        common_nodes.extend([node for sys in systems
                             for node in sys.postproc.nodes])
        '''
        common_nodes.extend([node for sys in systems
                             for eq in sys.eqs
                             for node in eq.eq_tree])
        '''
        common_replacers.extend([replacer
                                 for sys in systems
                                 for replacer in sys.postproc.replacers])

        # sinch all:
        delay_postproc(common_replacers, common_nodes)

        delays_data = self._get_delays_data(common_replacers, common_nodes)
        return(delays_data)
    
    def _get_delays_data(self, replacers_list, nodes_lists):

        '''Extract delay data from all nodes'''

        delays_data = []
        for i, node_list in enumerate(nodes_lists):
            for node in node_list:
                try:
                    data = replacers_list[i].get_output_data(node)
                    if data is not None:
                        # data = node.output.cpp.global_data
                        try:
                            delay_data = [data['converted_delay'],
                                          data['delay_data']]
                            delays_data.append(delay_data)
                        except KeyError:
                            pass
                except AttributeError:
                    pass

        return(delays_data)
    
    def show_nodes_global_data(self):
        
        for i, nodes_list in enumerate(self.nodes):
            for node in nodes_list:
                try:
                    data = self.replacers[i].get_output_data(node)
                    if data is not None:
                        print(data)
                    # print(node.output.cpp.global_data)
                except:
                    pass
