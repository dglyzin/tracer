from pandas import DataFrame
from collections import OrderedDict


class Plotter():
    def __init__(self, net):
        self.net = net

    def show(self, gout={}):
        out = OrderedDict()
        out['icCountArr'] = {
            'array': self.net.icCountArr,
            'frame': DataFrame([self.net.icCountArr])}

        icsDim = self.net.model.dimension - 1
        if icsDim == 0:
            columns = ["icDim", "source block", "dist block",
                       "source side", "dist side"]
            out['icList'] = {
                'array': self.net.icList,
                'frame': DataFrame(self.net.icList,
                                   columns=columns)}
        elif icsDim == 1:
            columns = ["icDim", "icLen", "source block",
                       "dist_block", "source side", "dist side",
                       "source offset", "dist offset"]
            out['icList'] = {
                'array': self.net.icList,
                'frame': DataFrame(self.net.icList,
                                   columns=columns)}

        blocks_ics_idxs = [dist_block for dist_block in self.net.blocks_ics]
        blocks_ics_table = [self.net.blocks_ics[dist_block]
                            for dist_block in blocks_ics_idxs]
        out['blocks_ics'] = {
            'frame': DataFrame(blocks_ics_table,
                               index=["dist_b%s" % str(dist_block)
                                      for dist_block in blocks_ics_idxs])}
        gout['ics'] = out
        return(gout)
        
