from gens.mini_solver.base_render import GenBaseRend


class GenCppRend(GenBaseRend):
    
    def __init__(self, net, hd_dir=None):
        GenBaseRend.__init__(self, hd_dir=hd_dir)

        self.net = net

    def get_out_for_mini_solver_cuda(self, params):
        '''
        DESCRIPTION:
        from set_params_for_definitions
            gridArgs list
            blocksArgs list
            paramsLen int
        
        from get_out_for_centrals
            params.centrals,

        from get_out_for_bounds
            params.bounds,

        from get_out_for_vertexs
            params.vertexs,

        from set_params_for_array:
            namesAndNumbers
             (only block0 value will be used)

        '''
        template = self.env.get_template('cuda/core.template')
        
        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'timeStep': params.timeStep,
    
            # get_out_for_centrals
            'centrals': params.centrals,

            # get_out_for_bounds
            'bounds': params.bounds,  # self.make_bounds_unique(params.bounds),

            'vertexs': params.vertexs,

            # get_out_for_array
            'namesAndNumbers': params.namesAndNumbers,

            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        
        return(out)

    def get_out_for_mini_solver_cpp_core(self, params):
        '''
        DESCRIPTION:
        from set_params_for_definitions
            gridArgs list
            blocksArgs list
            paramsLen int

        from set_params_for_array:
            namesAndNumbers
             (only block0 value will be used)

        '''
        template = self.env.get_template('cpp/core_h.template')
        
        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'timeStep': params.timeStep,

            # get_out_for_array
            'namesAndNumbers': params.namesAndNumbers,

            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        
        return(out)

    def get_out_for_mini_solver_cpp_kernels(self, params):
        template = self.env.get_template('cpp/kernels_cpp.template')

        args = {
            # get_out_for_array
            'namesAndNumbers': params.namesAndNumbers,
    
            # get_out_for_centrals
            'centrals': params.centrals,

            # get_out_for_bounds
            'bounds': params.bounds,  # self.make_bounds_unique(params.bounds),
            
            'vertexs': params.vertexs,

            'enumerate': enumerate,
            'len': len
        }
        
        # args like in dict()
        out = template.render(args)
        
        return(out)

    def get_out_for_mini_solver_cpp_solver(self, params):
        '''For that case there is no args so it used just
        for rendering solver_cpp.template to solver.cpp file
        (because otherwise it will be removed for sake of .gitignore).
        '''
        template = self.env.get_template('cpp/solver_cpp.template')

        args = {
        }
        
        # args like in dict()
        out = template.render(args)
        
        return(out)

    
