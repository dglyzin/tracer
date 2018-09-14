from gens.hs.env.centrals.cent_common import GenCommon
from gens.hs.env.centrals.cent_cpp_rend import GenCppRend
from gens.hs.env.centrals.cent_dom import GenDom
 

class Gen():

    '''
    Fill self.params for centrals functions template::

    (see ``self.set_params_for_centrals``)

    Generate cpp::

    (see ``get_out_for_centrals``)
    '''

    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommon(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)

        self.dom = GenDom(self)
