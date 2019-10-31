class BlockBase():
    def __init__(self, net, name, blockNumber):
        self.name = name
        self.net = net
        self.net.blockNumber = blockNumber

    def set_default(self):
        self.net.defaultEquation = 0
        self.net.defaultInitial = 0
        self.net.equationRegions = []
        self.net.boundRegions = []
        self.net.initialRegions = []
            
