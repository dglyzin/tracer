from pandas import DataFrame
from collections import OrderedDict


class Plotter():
    def __init__(self, net):
        self.net = net

    def show(self, gout={}):
        out = OrderedDict()
        out['blockCountArr'] = {
            'array': self.net.blockCountArr,
            'frame': DataFrame([self.net.blockCountArr])}
        
        # FOR blockPropArrList columns:
        columns = ["nodeIdx", "DeviceType", "DeviceIdx"]
        columns.append('cellOffsetX')
        
        domainDim = self.net.model.dimension

        if domainDim > 1:
            columns.append('cellOffsetY')
        if domainDim > 2:
            columns.append('cellOffsetZ')
        columns.append('cellCountX')
        
        if domainDim > 1:
            columns.append('cellCountY')
        if domainDim > 2:
            columns.append('cellCountZ')
        # END FOR

        out['blockPropArrList'] = {
            'array': self.net.blockPropArrList,
            'frame': DataFrame(self.net.blockPropArrList,
                               columns=columns)}

        out['blockInitFuncArrList'] = {
            'array': self.net.blockInitFuncArrList,
            'frame': DataFrame(self.net.blockInitFuncArrList)}

        out['blockCompFuncArrList'] = {
            'array': self.net.blockCompFuncArrList,
            'frame': DataFrame(self.net.blockCompFuncArrList)}

        gout['blocks'] = out
        return(gout)
