from translator.tree.maps import map_tree, map_tree_postproc, flatten

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('equation.tree')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class NetEditor():
    def __init__(self, net):

        self.net = net
        
    def map_out(self, replacer):

        '''Add out to self.eq_net (from self.parse)'''

        _map = map_tree(str(['s']), replacer)
        _map_postproc = map_tree_postproc(_map, replacer)
        return(_map_postproc)

    def flatten(self, key="original"):
        replacer = self.net.replacer.cpp.gen
        out = flatten(replacer, str(['s']), replacer.get_extractor(key))
        return(out)
