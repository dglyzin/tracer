from gens.hs.env.bounds.d1.bounds_common import GenCommon as GenCommonD1
from gens.hs.env.bounds.d1.bounds_cpp_rend import GenCppRend as GenCppRendD1
from gens.hs.env.bounds.d1.bounds_d1_dom import GenDomD1
 
    
class GenD1():
    '''
    Fill self.params for bound 1d template:
    (see self.set_params_for_bounds)

    Generate cpp:
    (see get_out_for_bounds)
    '''
    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommonD1(self)
        
        # cpp template render:
        self.cpp_render = GenCppRendD1(self)

        self.dom = GenDomD1(self)


class GenD2():
    '''
    Fill self.params for bound 2d template:
    (see self.set_params_for_bounds)

    Generate cpp:
    (see get_out_for_bounds)
    '''
    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommonD2(self)
        
        # cpp template render:
        self.cpp_render = GenCppRendD2(self)

        self.dom = GenDomD2(self)
