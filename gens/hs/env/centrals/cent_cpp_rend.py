from gens.hs.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):
    
    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_centrals(self):
        template = self.env.get_template('central_functions.template')

        args = {
            'equations': self.net.params,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

