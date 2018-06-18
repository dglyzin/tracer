from gens.hs.env.params.params_cpp import GenCpp
from gens.hs.env.params.params_cpp_rend import GenCppRend


class Gen():
    
    '''Generate cpp for params
    with templates'''

    '''
    Fill model.blocks params for initials template:
    (see self.cpp.set_params_for_initials)

    Generate cpp:
    (see self.cpp_render.get_out_for_initials)
    '''

    def __init__(self):
        # common for cpp and dom:
        self.cpp = GenCpp(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)
