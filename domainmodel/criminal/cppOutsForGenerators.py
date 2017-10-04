from jinja2 import Environment, FileSystemLoader


class CppOutsForGenerators():
    '''
    DESCRIPTION:

    '''
    def __init__(self):
        # self.params = params
        pathToTemplates = 'domainmodel/criminal/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate

    def make_bounds_unique(self, bounds):
        def unique_generator(bounds):
            unique = []
            for bound in bounds:
                if bound.funcName not in unique:
                    unique.append(bound.funcName)
                    yield(bound)
        return([bound for bound in unique_generator(bounds)])

    def get_out_for_mini_solver_cuda(self, params):
        '''
        DESCRIPTION:
        from set_params_for_definitions
            gridArgs list
            blocksArgs list
            paramsLen int
        
        from get_out_for_centrals
            params.equations,

        from get_out_for_bounds
            params.bounds,

        from set_params_for_array:
            namesAndNumbers
             (only block0 value will be used)

        '''
        template = self.env.get_template('mini_solver/cuda/core.template')
        
        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'timeStep': params.timeStep,
    
            # get_out_for_centrals
            'equations': params.equations,

            # get_out_for_bounds
            'bounds': self.make_bounds_unique(params.bounds),

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
        template = self.env.get_template('mini_solver/cpp/core_h.template')
        
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
        template = self.env.get_template('mini_solver/cpp/kernels_cpp.template')

        args = {
            # get_out_for_array
            'namesAndNumbers': params.namesAndNumbers,
    
            # get_out_for_centrals
            'equations': params.equations,

            # get_out_for_bounds
            'bounds': self.make_bounds_unique(params.bounds),

            'enumerate': enumerate,
            'len': len
        }
        
        # args like in dict()
        out = template.render(args)
        
        return(out)

    def get_out_for_definitions(self, params):
        template = self.env.get_template('definitions.template')

        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_array(self, params):
        '''
        DESCRIPTION:
        params.set_params_for_array must be called first.
        '''
        template = self.env.get_template('array.template')

        args = {
            'namesAndNumbers': params.namesAndNumbers,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_centrals(self, params):
        template = self.env.get_template('central_functions.template')

        args = {
            'equations': params.equations,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_interconnects(self, params):
        template = self.env.get_template('interconnects.template')

        args = {
            'ics': params.ics,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_vertex_2d(self, params):
        template = self.env.get_template('vertex_conditions.template')

        args = {
            'bounds': params.bounds_vertex,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_bounds(self, params):
        template = self.env.get_template('bound_conditions.template')

        args = {
            'bounds': self.make_bounds_unique(params.bounds),
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_parameters(self, params):
        template = self.env.get_template('params.template')

        args = {
            'params': params.parameters,
            'paramValues': params.parametersVal,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_initials(self, params):
        template = self.env.get_template('initial_conditions.template')

        args = {
            'blocks': params.blocks,
            'dim': params.dim,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)
