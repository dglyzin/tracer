from envs.hs.block.interval import Interval

from copy import deepcopy as copy
from copy import copy as weak_copy

from pandas import DataFrame

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('side.py')
logger.setLevel(level=log_level)


class Side():
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
                 default_size=None):
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

        self.split_side()

    def __repr__(self):
        try:
            rs = [list(i) for i in self.interval]
            ns = [(i.name['b'], i.name['e']) for i in self.interval]
        except AttributeError:
            raise(BaseException("split_side firts"))
            
        out = str(DataFrame([ns, rs], index=['bound/eq', 'range']))
        return(out)

    def has_interval(self):
        try:
            self.interval
        except AttributeError:
            return(False)
        return(True)

    def split_side(self, rewrite=False):
        
        '''If rewrite False, check if interval exist.'''
        
        if not rewrite and self.has_interval():
            return(self.interval)
        else:
            
            # try:
            return(self._split_side())
            # except AttributeError:
            #    raise(BaseException("set up block first"))

    def _split_side(self):
        '''
        TODO: use local regions (instead of block ones).
        DESCRIPTION:
        Separate side at intervals according existing regions.
        This function using equationRegions and boundRegions
        from self.block.

        Return
        [interval([from, to], name={e: eqNum, b: boundNum})
            | for each bRegion and eRegion from this side
                where interval.name[e] will be equation number
                    and interval.name[b] bound number]
        (see Interval class for more about interval's intersection)
        '''
        logger.debug("FROM split_side")
        side_num = self.side_num
        bRegions = []
        eRegions = []
        block = self.block
        if block is not None:
            bRegions = block.boundRegions[side_num]
            eRegions = block.equationRegions
            den = self.block.defaultEquation
        else:
            bRegions = self.bRegions
            eRegions = self.eRegions
            den = 0

        block_size = self._choice_block_size(bRegions, eRegions)
        _from, _to = self._choice_regions_intervals_gen()

        # find equation regions for side
        eRegionsForSide = [eRegion for eRegion in eRegions
                           if self._test_region_exist(eRegion, side_num)]

        logger.debug("eRegionsForSide")
        logger.debug(eRegionsForSide)

        # find bound region for side
        bRegionsForSide = [bRegion for bRegion in bRegions
                           if bRegion.side_num == side_num]

        logger.debug("bRegionsForSide")
        logger.debug(bRegionsForSide)

        sInterval = Interval([0.0, block_size], name={'b': None, 'e': den})

        bIntervals = [Interval([_from(bRegion), _to(bRegion)],
                               name={'b': bRegion.boundNumber})
                      for bRegion in bRegionsForSide]

        bIntervals = sInterval.split_all(bIntervals, [])

        logger.debug("bIntervals")
        logger.debug(bIntervals)

        '''
        for bInterval in bIntervals:
            print_dbg(bInterval.name)
        '''
        eIntervals = [Interval([_from(eRegion), _to(eRegion)],
                               name={'e': eRegion.equationNumber})
                      for eRegion in eRegionsForSide]

        logger.debug("eIntervals")
        logger.debug(eIntervals)

        oIntervals = []
        for bInterval in bIntervals:
            oIntervals.extend(bInterval.split_all(copy(eIntervals), []))

        logger.debug("for side")
        logger.debug(side_num)

        logger.debug("oIntervals")
        logger.debug(oIntervals)

        self.interval = oIntervals

        new_side = {'side_num': side_num,
                    # 'blockNumber': block.blockNumber,
                    'side_data': oIntervals}
        return(new_side)

    def _choice_block_size(self, bRegions, eRegions):
        
        '''Extract block size according to side_num.
        If block given, use it, else try to use regions
        for calculate size. At last use self.default_size.'''
        
        side_num = self.side_num
        block = self.block

        def extract_from_regions(bRegions, eRegions, sides_nums):

            '''Try to extract size from regions, according sides_nums'''

            regions = ([bRegion for bRegion in bRegions
                        if bRegion.side_num in sides_nums] + eRegions)
            if sides_nums == [0, 1]:
                block_size = max([region.yto for region in regions])
            elif sides_nums == [3, 2]:
                block_size = max([region.xto for region in regions])
            return(block_size)

        if side_num in [0, 1]:
            sides_nums = [0, 1]
            if block is not None:
                block_size = block.size.sizeY
        elif side_num in [3, 2]:
            sides_nums = [3, 2]
            if block is not None:
                block_size = block.size.sizeX

        if block is None:
            try:
                block_size = extract_from_regions(bRegions, eRegions,
                                                  sides_nums)
            except ValueError:
                try:
                    block_size = self.default_size
                except AttributeError:
                    raise(BaseException(("give either block "
                                         + "or self.default_size"
                                         + "or regions")))
        return(block_size)

    def _choice_regions_intervals_gen(self):
        side_num = self.side_num

        if side_num in [0, 1]:
            # case for [0, y] or [x_max, y]

            _from = lambda region: region.yfrom
            _to = lambda region: region.yto

        elif(side_num in [3, 2]):
            # case for [x, y_max] or [x, 0]

            _from = lambda region: region.xfrom
            _to = lambda region: region.xto

        return((_from, _to))

    def _test_region_exist(self, eRegion, side_num):
        '''
        DESCRIPTION:
        Test if equation region exist for this side.
        '''
        if self.block is not None:
            if self.block.size.dimension == 1:
                return(True)

        if side_num == 0:
            # test for [0, y]
            return(eRegion.xfrom == 0.0)  # eRegion.xto == 0.0
        elif(side_num == 3):
            # test for [x, y_max]
            return(eRegion.yto == self.block.size.sizeY)
        elif(side_num == 1):
            # test for [x_max, y]
            return(eRegion.xto == self.block.size.sizeX)
        elif(side_num == 2):
            # test for [x, 0]
            return(eRegion.yfrom == 0.0)  # eRegion.yto == 0.0

    def set_block(self, block):
        self.block = block
        self.split_side(rewrite=True)

    def add_bound_region(self, bRegion):

        '''Add region to side and it's block'''

        if bRegion not in self.bRegions:
            self.bRegions.append(bRegion)
            self.split_side(rewrite=True)

        # depricated
        # if self.block is not None:
        #    self.block.sinch_side_regions(self)

    def add_eq_region(self, eRegion):
        side_num = self.side_num
        if self._test_region_exist(eRegion, side_num):
            self.split_side(rewrite=True)
        
