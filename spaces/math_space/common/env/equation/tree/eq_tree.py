from translator.tree.maps import map_tree, map_tree_postproc

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


class EqTree():
    def __init__(self, net):

        self.net = net

    def map_out(self, replacer):

        '''Add out to self.eq_tree (from self.parse)'''

        _map = map_tree(self.net.eq_tree, replacer)
        _map_postproc = map_tree_postproc(_map, replacer)

        # if brackets was added to left part of equation
        # like U'= -> (U')=
        # then remove them:
        # from '='->[br-> ['(', args->[a], ')'], right]
        # to '='-> [a, right]:
        if self.net._left_brs_added:
            br_child = _map_postproc.children[1]
            child = br_child.children[1].children[0]
            _map_postproc.replace_child(br_child, child)
            self.net._left_brs_added = False

        return(_map_postproc)

    def flatten(self, key):

        '''Return list of term as key.
        Key either original or cpp.
        Flatten is only work after map_*'''
        '''
        if key == 'cpp':
            kernel = self.map_cpp()
        elif key == 'original':
            kernel = self.eq_tree
        elif key == 'rand':
            kernel = self.eq_tree
        elif key == 'sympy':
            kernel = self.map_sympy()
        '''
        kernel = self.net.eq_tree

        logger.debug("kernel")
        logger.debug(kernel)
        
        out_kernel = kernel.flatten(key)
            
        return("".join(out_kernel))
