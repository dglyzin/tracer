class icBase():
    def __init__(self, net, name,
                 blockNumber1=0, blockNumber2=1,
                 block1Side=0, block2Side=1):
        self.name = name
        self.net = net

        self.net.block1 = blockNumber1
        self.net.block2 = blockNumber2
        self.net.block1Side = block1Side
        self.net.block2Side = block2Side
