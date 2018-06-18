from gens.hs.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):

    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_definitions(self):
        template = self.env.get_template('definitions.template')
        params = self.net.params

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
