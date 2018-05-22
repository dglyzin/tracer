from envs.hs.block.side.side_editor import SideEditor
from envs.hs.block.side.side_separator import SideSeparator
from pandas import DataFrame

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('side.py')
logger.setLevel(level=log_level)


class SideNet():
    '''
    ***x->
    *  
    |  ---side 2---
    y  |          |
       s          s
       i          i
       d          d
       e          e
       0          1
       |          |
       ---side 3---
    '''
    def __init__(self, side_num, block=None,
                 bRegions=None, eRegions=None,
                 default_size=None, dim=2):

        self.editor = SideEditor(self)
        self.separator = SideSeparator(self)

        self.dim = dim

        if bRegions is None:
            bRegions = []
        if eRegions is None:
            eRegions = []
        
        logger.debug("bRegions")
        logger.debug(bRegions)
        
        for bRegion in bRegions:
            if side_num != bRegion.side_num:
                raise(BaseException("side_num must be equal "
                                    + "in Side and all it's boundRegions"))

        self.block = block

        if default_size is not None:
            self.default_size = default_size

        self.side_num = side_num
        
        self.bRegions = bRegions
        self.eRegions = eRegions

        # add side_num to all regions:
        for bRegion in self.bRegions:
            bRegion.side = self.side_num

        self.separator.split_side()

    def __repr__(self, notebook=False):
        try:
            rs = [list(i) for i in self.interval]
            ns = [(i.name['b'], i.name['e']) for i in self.interval]
        except AttributeError:
            raise(BaseException("split_side firts"))
        
        if notebook:
            out = DataFrame([ns, rs], index=['bound/eq', 'range'])
        else:
            out = str(DataFrame([ns, rs], index=['bound/eq', 'range']))
        return(out)
