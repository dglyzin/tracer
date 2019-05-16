from functools import reduce


class Postproc():
    def __init__(self, net):
        self.net = net

    def postproc_dirichlet(self, params_of_gens):

        '''If btype is 0 use Dirichlet
        i.e. bound values for whole equation's right side's'''

        all_params = reduce(lambda acc, x: acc+[param for param in x],
                            params_of_gens, [])
        for i, param in enumerate(all_params):
            if param.btype == 0:
                
                # replace right side with border_values:
                prefixs = [pv[:pv.find("=")+1]
                           for pv in param.parsedValues]
                param.parsedValues = [prefix+param.border_values_parsed[idx]
                                      for idx, prefix in enumerate(prefixs)]
            # print(param.parsedValues)

    def postporc_delays(self, params_of_gens):

        '''Sinch delays in all equations in all systems.
        Change gen.params.parsedValues for gen in gens.
        Return delays data for each variable (U, V, ...)'''

        all_params = reduce(lambda acc, x: acc+[param for param in x],
                            params_of_gens, [])

        eSystems = [param.equation for param in all_params]

        for eSystem in eSystems:
            # collect all nodes in one place
            # for each system
            # (system.postproc.nodes):
            eSystem.postproc.collect_nodes()

        # sinch systems:
        delays_data = eSystems[0].postproc.postproc_delay_sys(eSystems[1:])
        # print("delays_data:")
        # print(delays_data)

        delays = {}
        for delay, source_data in delays_data:
            term_var = source_data[1][0]
            # print("source_data")
            # print(source_data[1][0])

            if term_var not in delays:
                delays[term_var] = [delay]
            else:
                if delay not in delays[term_var]:
                    delays[term_var].append(delay)
        # logger.info("delays:")
        # logger.info(delays)

        # print("all parsedValues:")
        # change parsed values:
        for i, param in enumerate(all_params):
            param.parsedValues = [eq.show_cpp()
                                  for eq in eSystems[i].eqs]
            # print(param.parsedValues)

        return(delays)
