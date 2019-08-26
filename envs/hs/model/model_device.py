
import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('model_main.model_device')

# if using directly uncoment that:
'''
# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('model_main')
logger.setLevel(level=log_level)
'''


class ModelDevice():

    def __init__(self, net):
        self.net = net

    # FOR Computation nodes
    def deleteCompnode(self, index):
        del self.net.compnodes[index]

    def deleteAllCompnodes(self):
        self.net.compnodes = []

    def getDeviceCount(self):
        return sum([node.cpuCount+node.gpuCount
                    for node in self.net.compnodes])

    def getNodeCount(self):
        return len(self.net.compnodes)

    def getNodeSpec(self):
        '''
        returns parameter string to slurm:
        -w cnode_x cnode_y ...
        if node.name == "any" (or "*") for first node,
        or self.net.compnodes is empty
        then empty string return
        '''
        
        paramLine = "-w "
        
        if len(self.net.compnodes) == 0:
            return ""
        elif len(self.net.compnodes) == 1:
            node = self.net.compnodes[0]
            if node.name in ("any", "*"):
                return ""
            else:
                paramLine += node.name
        else:
            for node in self.net.compnodes:
                if node.name in ("any", "*"):
                    raise(BaseException(
                        'One of Hardware node Name is "any" or "*"'
                        + '\n but there is other nodes here!'
                        + '\n Remove them if all computation nodes needed'))
                paramLine += node.name + ","
            paramLine = paramLine[:-1]
        return(paramLine)
    # END FOR

    def getDeviceStateSize(self, nodeIdx, deviceType, deviceIdx):
        '''
        counts state sizes for every block that is scheduled
        to a given node and a given device
        '''
        devStateSize = 0
        for (blockIdx, block) in enumerate(self.net.blocks):
            mapping = self.net.mapping[blockIdx]
            if ((nodeIdx == mapping["NodeIdx"])
                and (deviceType == mapping["DeviceType"])
                and (deviceIdx == mapping["DeviceIdx"])):
                cellCount = block.size.getCellCount(self.net.grid.gridStepX,
                                                    self.net.grid.gridStepY,
                                                    self.net.grid.gridStepZ)
                cellCountFull = cellCount[0]*cellCount[1]*cellCount[2]
                devStateSize += cellCountFull*self.net.base.getCellSize()
        return devStateSize
    
    def getMaxStatesCount(self):
        '''
        returns maximum number of states that can be
        stored in memory by ANY computing device
        result = min_{for every computing device D}
                     (D.memory/sum_{for every block B inside D} (B.total) )
        '''
        minCapacity = 0
        for nodeIdx, node in enumerate(self.net.compnodes):
            for cpuIdx in range(node.cpuCount):
                memorySize = node.cpuMemory[cpuIdx]
                devStateSize = self.getDeviceStateSize(nodeIdx, "cpu", cpuIdx)
                if devStateSize > 0:
                    capacity = int(memorySize * 1024 * 1024 * 1024/(8 * devStateSize))
                    if (minCapacity == 0) or (capacity < minCapacity):
                        minCapacity = capacity
                else:
                    capacity = "infinity"
                print_args = (node.name, "cpu", cpuIdx,
                              memorySize, devStateSize, capacity)
                logger.info(("For node {} {}{} memory is {}GB,"
                             + " total state size is {} elems,"
                             + " capacity={}.").format(*print_args))
            for gpuIdx in range(node.gpuCount):
                memorySize = node.gpuMemory[gpuIdx]
                devStateSize = self.getDeviceStateSize(nodeIdx, "gpu", gpuIdx)
                if devStateSize > 0:
                    capacity = int(memorySize * 1024 * 1024 * 1024/(8 * devStateSize))
                    if (minCapacity == 0) or (capacity < minCapacity):
                        minCapacity = capacity
                else: 
                    capacity = "infinity"
                print_args = (node.name, "gpu", gpuIdx,
                              memorySize, devStateSize, capacity)
                logger.info(("For node {} {}{} memory is {}GB,"
                             + " total state size is {} elems,"
                             + " capacity={}.").format(*print_args))
                    
        return minCapacity  # like 100*100*100 000 elements = 8GB < 64GB
