from gens.hs.env.initials.initials_cpp import GenCpp
from gens.hs.env.initials.initials_cpp_rend import GenCppRend


class Gen():
    
    '''Generate cpp for initials
    with templates'''

    '''
    Fill model.blocks params for initials template:
    (see self.cpp.set_params_for_initials)

    Generate cpp:
    (see self.cpp_render.get_out_for_initials)
    '''

    def __init__(self):
        # for cpp:
        self.cpp = GenCpp(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)

