from gens.hs.env.definitions.def_common import GenCommon
from gens.hs.env.definitions.def_cpp_rend import GenCppRend


class Gen():
    
    '''Generate cpp for definitions
    with templates'''

    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommon(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)

