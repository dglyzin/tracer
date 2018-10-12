from gens.hs.env.initials.initials_cpp import GenCpp
from gens.hs.env.initials.initials_cpp_rend import GenCppRend


import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('initials_main.initials_cpp')

# if using directly uncoment that:
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('initials_main')
logger.setLevel(level=log_level)



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

