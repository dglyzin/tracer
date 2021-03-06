from gens.hs.gen_env.cpp.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):
    
    def __init__(self, net):

        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_bounds(self, vertex=False):

        if not vertex:
            template = self.env.get_template('bound_conditions.template')
            bounds = self.net.params.bounds_edges
        else:
            template = self.env.get_template('vertex_conditions.template')
            bounds = self.net.params.bounds_vertex

        args = {
            'bounds': self.make_bounds_unique(bounds),
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def make_bounds_unique(self, bounds):
        def unique_generator(bounds):
            unique = []
            for bound in bounds:
                if bound.funcName not in unique:
                    unique.append(bound.funcName)
                    yield(bound)
        return([bound for bound in unique_generator(bounds)])
