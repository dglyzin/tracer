class SideEditor():
    def __init__(self, net):
        self.net = net

    def get_dim(self):
        if self.net.block is not None:
            return(self.net.block.size.dimension)
        else:
            try:
                return(self.net.dim)
            except AttributeError:
                raise(BaseException("Set dimension with set_dim"
                                    + " or get block"))

    def set_dim(self, dim):
        self.net.dim = dim

    def set_block(self, block):
        self.net.block = block
        self.net.separator.split_side(rewrite=True)

    def add_bound_region(self, bRegion):

        '''Add region to side and it's block'''

        if bRegion not in self.net.bRegions:
            self.net.bRegions.append(bRegion)
            self.net.separator.split_side(rewrite=True)

        # depricated
        # if self.block is not None:
        #    self.block.sinch_side_regions(self)

    def add_eq_region(self, eRegion):
        side_num = self.net.side_num
        if self.net.separator._test_region_exist(eRegion, side_num):
            self.net.separator.split_side(rewrite=True)
        
