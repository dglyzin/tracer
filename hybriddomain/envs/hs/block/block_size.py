from hybriddomain.spaces.some_space.someFuncs import getCellCountInClosedInterval
from hybriddomain.spaces.some_space.someFuncs import getCellCountInHalfInterval


class BlockSize():
    def __init__(self, net):
        self.net = net

    def __repr__(self):
        out = ""
        '''
        attrs = self.__dict__
        for key_atr in attrs.keys():
            out += key_atr + ": " + str(attrs[key_atr]) + "\n"
        '''
        out += "dim: " + str(self.dimension)
        out += "offsetX: " + str(self.offsetX)
        out += "sizeX: " + str(self.sizeX)
        out += "gridStepX: " + str(self.gridStepX)
        
        if self.dimension > 1:
            out += "offsetY: " + str(self.offsetY)
            out += "sizeY: " + str(self.sizeY)
            out += "gridStepY: " + str(self.gridStepY)
            
        if self.dimension > 2:
            out += "offsetZ: " + str(self.offsetZ)
            out += "sizeZ: " + str(self.sizeZ)
            out += "gridStepZ: " + str(self.gridStepZ)
        
        return(out)

    def set_default(self, dimension=1):
        self.dimension = dimension
        self.offsetX = 0.0
        self.sizeX = 1.0
        self.gridStepX = 1.0
        
        if self.dimension > 1:
            self.offsetY = 0.0
            self.sizeY = 1.0
            self.gridStepY = 1.0
            
        if self.dimension > 2:
            self.offsetZ = 0.0
            self.sizeZ = 1.0
            self.gridStepZ = 1.0

    def getCellCount(self, dx, dy, dz):
        '''
        TODO
        При вычислении количества ячеек блока нужно учитывать,
        что формула их расчета:
           ДлинаБлока / ШагПоПространсту + 1
        Если блок от 0 до 1, а шаг 0,1, то расчет без прибавления 1 даст 10
        В таком случае последняя точка будет иметь индект 9 и координату 0,9,
        что неверно.
        Если выполнить прибавление 1, то точек будет 11, и последняя будет
        иметь индекс 10 и координа 1
        Изменение функции getCellCountAlongLine делать нельзя, так как она
        занимается расчетом и значений сдвигов, которые не подчиняются
        правилу выше.
        Необходимо убедиться, что изменение ниже (+1 ко всем координатам,
        если они актуальны) правильное.
        '''
        yc, zc = 1, 1
        xc = getCellCountInClosedInterval(self.sizeX, dx)
        if self.dimension > 1:
            yc = getCellCountInClosedInterval(self.sizeY, dy)
        if self.dimension > 2:
            zc = getCellCountInClosedInterval(self.sizeZ, dz)
        return [xc, yc, zc]

    def getCellOffset(self, dx, dy, dz):
        # TODO complete
        yc, zc = 1, 1
        xc = getCellCountInHalfInterval(self.offsetX, dx)
        if self.dimension > 1:
            yc = getCellCountInHalfInterval(self.offsetY, dy)
        if self.dimension > 2:
            zc = getCellCountInHalfInterval(self.offsetZ, dz)
        # print("block", self.name)
        # print self.offsetX, self.offsetY
        return [xc, yc, zc]

    def get_cell_size(self, model):
        # count of equation in each cell
        # (storage of each cell is count of equations in block)
        return(len(model.equations[self.net.defaultEquation].eqs))
