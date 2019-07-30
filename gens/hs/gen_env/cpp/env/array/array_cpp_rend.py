from gens.hs.gen_env.cpp.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):

    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_array(self):
        '''
        DESCRIPTION::

        ``params.set_params_for_array`` must be called first.
        '''
        template = self.env.get_template('array.template')
        params = self.net.params
        args = {
            'namesAndNumbers': params.namesAndNumbers,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

