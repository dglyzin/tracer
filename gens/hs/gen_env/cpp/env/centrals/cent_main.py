from gens.hs.gen_env.cpp.env.centrals.cent_common import GenCommon
from gens.hs.gen_env.cpp.env.centrals.cent_cpp_rend import GenCppRend

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.cent_common')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('cent_main')
logger.setLevel(level=log_level)
 

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
