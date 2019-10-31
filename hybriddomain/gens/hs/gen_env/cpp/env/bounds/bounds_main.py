from hybriddomain.gens.hs.gen_env.cpp.env.bounds.d1.bounds_common import GenCommon as GenCommonD1
from hybriddomain.gens.hs.gen_env.cpp.env.bounds.d2.bounds_2d import GenCommon as GenCommonD2

from hybriddomain.gens.hs.gen_env.cpp.env.bounds.common.bounds_cpp_rend import GenCppRend


import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('bounds.bounds_common')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('bounds.bounds_main')
logger.setLevel(level=log_level)

    
class GenD1():
    '''
    Fill ``self.params`` for bound 1d template::

    (see ``self.set_params_for_bounds``)

    Generate cpp::

    (see ``get_out_for_bounds``)
    '''
    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommonD1(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)


class GenD2():
    '''
    Fill ``self.params`` for bound 2d template::

    (see self.set_params_for_bounds)

    Generate cpp::

    (see ``get_out_for_bounds``)
    '''
    def __init__(self):
        # common for cpp and dom:
        self.common = GenCommonD2(self)
        
        # cpp template render:
        self.cpp_render = GenCppRend(self)
