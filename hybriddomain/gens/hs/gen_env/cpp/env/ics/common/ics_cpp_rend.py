from hybriddomain.gens.hs.gen_env.cpp.env.base.base_render import GenBaseRend


class GenCppRend(GenBaseRend):
    
    def __init__(self, net):
        GenBaseRend.__init__(self)

        self.net = net

    def get_out_for_interconnects(self):
        template = self.env.get_template('interconnects.template')

        args = {
            'ics': self.net.params.ics,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    
