from gens.hs.env.ics.d1.ics_d1_common import GenCommonD1
from gens.hs.env.ics.d2.ics_d2_common import GenCommonD2

from gens.hs.env.ics.common.ics_cpp_rend import GenCppRend
 
from gens.hs.env.ics.common.ics_dom import GenDomCommon

    
class GenD1():
    '''
    Fill ``self.params`` for ics template::

    (see ``self.set_params_for_interconnects``)

    Generate cpp::

    (see ``get_out_for_interconnects``)
    '''
    def __init__(self):
        # common for cpp and dom:
        # (parse equations, fill namesAndNumbers)
        self.common = GenCommonD1(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)

        # fill functionMap:
        self.dom = GenDomCommon(self)


class GenD2():
    '''
    Fill ``self.params`` for ics template::

    (see ``self.set_params_for_interconnects``)

    Generate cpp::

    (see ``get_out_for_interconnects``)
    '''
    def __init__(self):
        # common for cpp and dom:
        # (parse equations, fill namesAndNumbers)
        self.common = GenCommonD2(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)

        # fill functionMap:
        self.dom = GenDomCommon(self)


