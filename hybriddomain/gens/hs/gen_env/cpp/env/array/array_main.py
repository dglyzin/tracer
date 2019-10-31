from hybriddomain.gens.hs.gen_env.cpp.env.array.array_common import GenCommon
from hybriddomain.gens.hs.gen_env.cpp.env.array.array_cpp_rend import GenCppRend


class Gen():
    '''
    Fill ``self.namesAndNumbers`` for array template::

    (see ``self.set_params_for_array``)

    Generate cpp::

    (see ``get_out_for_array``)
    '''

    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommon(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)
