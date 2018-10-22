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

        self.nodes = [node for eq in self.net.eqs
                      for node in eq.eq_tree]
    
    def postproc_delay_nodes(self):

        '''Postproc delays in all eqs.
        self.nodes must exist (from collect_nodes method)'''

        delay_postproc(self.nodes)

    def postproc_delay_sys(self, systems):

        '''postproc delays in all eqs in all systems'''

        # add self.nodes to global:
        common_nodes = self.nodes[:]
        
        # add other systems nodes to global:
        common_nodes.extend([node for sys in systems
                             for eq in sys.eqs
                             for node in eq.eq_tree])

        # sinch all:
        delay_postproc(common_nodes)

        delays_data = self._get_delays_data(common_nodes)
        return(delays_data)
    
    def _get_delays_data(self, nodes):

        '''Extract delay data from all nodes'''

        delays_data = []
        for node in nodes:
            try:
                data = node.output.cpp.global_data
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

        for node in self.nodes:
            try:
                print(node.output.cpp.global_data)
            except:
                pass
