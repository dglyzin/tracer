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

        gout['ics'] = out
        return(gout)
        
