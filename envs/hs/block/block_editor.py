from envs.hs.block.side import Side
from envs.hs.block.vertex import Vertex


class BlockEditor():
    def __init__(self, net):
        self.net = net

    def set_sides_default(self):
        dim = self.net.size.dimension
        if dim == 1:
            sides_nums = [2]
        elif dim == 2:
            sides_nums = [0, 1, 2, 3]

        self.net.sides = dict([(side_num, Side(side_num, block=self.net))
                               for side_num in sides_nums])

        # sinch boundRegion dict:
        for side_num in self.net.sides:
            self.replace_block_regions(self.net.sides[side_num])

        # for side in self.net.sides:
        #    side.split_side()

    def init_regions(self):
        # boundRegions factorize at classes with
        # different sides_nums (i.e boundRegions[side_num]):
        side_nums = [0, 1, 2, 3]
        self.net.boundRegions = dict([(side_num, [])
                                      for side_num in side_nums])
        self.net.equationRegions = []
        self.net.initialRegions = []
        self.set_regions_defaults(0, 0, 0)

    def fill_regions(self, bRegions, eRegions, iRegions):

        '''Fill all regions. All sides must exist.'''

        # add bRegion from list:
        for bRegion in bRegions:
            self.add_bound_region(bRegion, bRegion.side)

        for eRegion in eRegions:
            self.add_eq_region(eRegion)

        self.net.initialRegions = iRegions

    def set_regions_defaults(self, deRegion, dbRegion, diRegion):

        self.net.defaultEquation = deRegion
        self.net.defaultInitial = dbRegion
        self.net.defaultBound = diRegion

    def set_vertexs(self):
        dim = self.net.size.dimension
        if dim == 1:
            self.net.vertexs = None
            vertexs_sides = [[0], [1]]
        elif dim == 2:
            vertexs_sides = [[0, 2], [2, 1], [1, 3], [3, 0]]
        self.net.vertexs = dict([(str(vertex),
                                  Vertex(vertex, self.net.sides, self.net))
                                 for vertex in vertexs_sides])

    def add_or_edit_side(self, side):

        '''Add or replace side in block.sides.
        All block.boundRegions[side.side_num] will
        be rewrited.'''

        index = self.edit_side(side)
        if index is not None:
            return(index)
        else:
            return(self.add_side(side))

    def edit_side(self, side):

        '''Replace side to self.net.sides,
        if side.side_num == self.net.sides[i] for
        some i. If side not found return None.'''

        # find side with side.side_num:
        if side.side_num in self.net.sides.keys():
            # change it:
            side.set_block(self.net)
            self.net.sides[side.side_num] = side

            # sinch boundRegion dict:
            self.replace_block_regions(side)
            side.split_side(rewrite=True)
            return(side.side_num)

        # if nothing found:
        return(None)

    def add_side(self, side):
        
        '''Add side to self.net.sides, if side whth
        side.side_num not exist. If otherwise return
        index of side in self.net.sizes.'''
        
        # if side exist:
        if side.side_num in self.net.sides.keys():
            print("side %d alredy exist" % (side.side_num))
            return(side.side_num)

        else:
            # if not:
            side.set_block(self.net)
            self.net.sides[side.side_num] = side
            
            # sinch boundRegion dict:
            self.replace_block_regions(side)
            side.split_side(rewrite=True)
            return(side.side_num)

    def replace_block_regions(self, side):

        '''Add region pointer from side to
        block.boundRegions[side_num]'''

        side_num = side.side_num
        self.net.boundRegions[side_num] = side.bRegions
        
    def sinch_side_regions_depricated(self, side):

        '''Add regions from side to block and backward
        (if they not exist alredy)'''

        side_num = side.side_num

        # sinch boundRegions:
        bRegionsS = side.bRegions

        if side_num in self.net.boundRegions:
            bRegionsB = self.net.boundRegions[side_num]
            bRegionsB.extend([bRegion for bRegion in bRegionsS
                              if bRegion not in bRegionsB])
            bRegionsS.extend([bRegion for bRegion in bRegionsB
                              if bRegion not in bRegionsS])
        else:
            self.net.boundRegions[side_num] = [bRegion for bRegion in bRegionsS]

        # sinch equations:
        eRegionsB = self.net.equationRegions
        eRegionsS = side.eRegions

        eRegionsB.extend([eRegion for eRegion in eRegionsS
                          if eRegion not in eRegionsB])
        eRegionsS.extend([eRegion for eRegion in eRegionsB
                          if eRegion not in eRegionsS])
        
        side.set_block(self.net)
        side.split_side(rewrite=True)
        
    def add_bound_region(self, bRegion):

        '''Add region to block.boundRegions[side_num]
        and to according side. Side must exist.'''

        side_num = bRegion.side_num
        self.net.sides[side_num].add_bound_region(bRegion)

        '''
        if side_num in self.net.boundRegions:
            if bRegion not in self.net.boundRegions[side_num]:
                self.net.boundRegions[side_num].append(bRegion)
                self.net.sides[side_num].split_side(rewrite=True)
        else:
            raise(BaseException("side %s not exist" % (str(side_num))))
        #    self.net.boundRegions[side_num] = [bRegion]
        '''
        # depricated:
        # self.sinch_side_regions(self.net.sides[side_num])

    def add_eq_region(self, eRegion):

        '''Add region to block'''

        if eRegion not in self.net.equationRegions:
            self.net.equationRegions.append(eRegion)
            for side_num in self.net.sides:
                self.net.sides[side_num].add_eq_region(eRegion)
                
    def sinch_sides(self):
        pass
