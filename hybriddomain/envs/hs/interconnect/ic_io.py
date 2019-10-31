from collections import OrderedDict


class icIO():
    def __init__(self, net):
        self.net = net

    def fillProperties(self, idict):
        self.net.base.name = idict["Name"]
        self.net.block1 = idict["Block1"]
        self.net.block2 = idict["Block2"]
        self.net.block1Side = idict["Block1Side"]
        self.net.block2Side = idict["Block2Side"]

    def getPropertiesDict(self):
        propDict = OrderedDict([
            ("Name", self.net.base.name),
            ("Block1", self.net.block1),
            ("Block2", self.net.block2),
            ("Block1Side", self.net.block1Side),
            ("Block2Side", self.net.block2Side)])
        return propDict
