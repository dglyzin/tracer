# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from regions import  *
from someFuncs import getCellCountInClosedInterval, getCellCountInHalfInterval
from objectsTemplate import Object


class Block(Object):
    def __init__(self, name, dimension):
        self.name = name
        self.dimension = dimension
        self.offsetX = 0.0
        self.sizeX = 1.0
        self.gridStepX = 1.0
        
        if self.dimension >1:
            self.offsetY = 0.0
            self.sizeY = 1.0
            self.gridStepY = 1.0
            
        if self.dimension >2:
            self.offsetZ = 0.0
            self.sizeZ = 1.0
            self.gridStepZ = 1.0
        
        self.defaultEquation = 0
        self.defaultInitial = 0
        self.equationRegions = []
        self.boundRegions = []
        self.initialRegions = []

    def getCellCount(self, dx, dy, dz ):        
        yc, zc = 1, 1
        #TODO При вычислении количества ячеек блока нужно учитывать, что формула их расчета
        #     ДлинаБлока / ШагПоПространсту + 1
        #     Если блок от 0 до 1, а шаг 0,1, то расчет без прибавления 1 даст 10
        #     В таком случае последняя точка будет иметь индект 9 и координату 0,9, что неверно
        #     Если выполнить прибавление 1, то точек будет 11, и последняя будет иметь индекс 10 и координа 1
        #     Изменение функции getCellCountAlongLine делать нельзя, так как она занимается расчетом и значений сдвигов,
        #     которые не подчиняются правилу выше
        #     Необходимо убедиться, что изменение ниже (+1 ко всем координатам, если они актуальны) правильное
        xc = getCellCountInClosedInterval(self.sizeX, dx) 
        if self.dimension >1:
            yc = getCellCountInClosedInterval(self.sizeY, dy) 
        if self.dimension >2:
            zc = getCellCountInClosedInterval(self.sizeZ, dz) 
        return [xc, yc, zc]

    def getCellOffset(self, dx, dy, dz ):
        #TODO complete
        yc, zc = 1, 1
        xc = getCellCountInHalfInterval(self.offsetX, dx) 
        if self.dimension >1:
            yc = getCellCountInHalfInterval(self.offsetY,dy)
        if self.dimension >2:
            zc = getCellCountInHalfInterval(self.offsetZ,dz)
        print "block", self.name
        #print self.offsetX, self.offsetY
        return [xc, yc, zc]
        
    def fillProperties(self, bdict):
        self.name = bdict["Name"]        
        self.offsetX = bdict["Offset"]["x"]
        self.sizeX = bdict["Size"]["x"]        
        if self.dimension > 1:
            self.offsetY = bdict["Offset"]["y"]
            self.sizeY = bdict["Size"]["y"]            
        if self.dimension > 2:
            self.offsetZ = bdict["Offset"]["z"]
            self.sizeZ = bdict["Size"]["z"]            
        
        self.defaultEquation = bdict["DefaultEquation"]
        self.defaultInitial = bdict["DefaultInitial"]
        
        self.boundRegions = []
        for boundDict in bdict["BoundRegions"]:
            self.boundRegions.append(BoundRegion(boundDict,self.dimension))
        for initDict in bdict["InitialRegions"]:
            self.initialRegions.append(InitialRegion(initDict,self.dimension))
        for equatDict in bdict["EquationRegions"]:
            self.equationRegions.append(EquationRegion(equatDict,self.dimension))		
    
    def getPropertiesDict(self):
        offsetDict = OrderedDict([("x", self.offsetX)])
        sizeDict = OrderedDict([("x", self.sizeX)])        
        if self.dimension > 1:
            offsetDict.update({"y":self.offsetY})
            sizeDict.update({"y":self.sizeY})            
        if self.dimension > 2:
            offsetDict.update({"z":self.offsetZ})
            sizeDict.update({"z":self.sizeZ})            
        propDict = OrderedDict([            
            ("Name", self.name),
            #("Dimension", self.dimension),
            ("Offset", offsetDict),
            ("Size", sizeDict),            
            ("DefaultEquation", self.defaultEquation),
            ("DefaultInitial", self.defaultInitial),
            ("BoundRegions", [bdict.getPropertiesDict(self.dimension) for bdict in  self.boundRegions]),
            ("InitialRegions", [idict.getPropertiesDict(self.dimension) for idict in  self.initialRegions]),
            ("EquationRegions", [edict.getPropertiesDict(self.dimension) for edict in  self.equationRegions])
        ])   
        return propDict
