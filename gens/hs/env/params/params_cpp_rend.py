from gens.hs.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):

    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_parameters(self):
        template = self.env.get_template('params.template')
        params = self.net.params

        args = {
            'params': params.parameters,
            'paramValues': params.parametersVal,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

