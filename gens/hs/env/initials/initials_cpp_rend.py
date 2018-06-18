from gens.hs.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):
    
    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_initials(self):
        template = self.env.get_template('initial_conditions.template')
        params = self.net.params

        args = {
            'blocks': params.blocks,
            'dim': params.dim,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)
