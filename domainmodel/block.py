# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from regions import  *

class Block(object):
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
        self.boundRegions = []
        self.initialRegions = []

    def getCellCount(self, dx, dy, dz ):
        #TODO complete
        yc, zc = 1, 1
        xc = self.sizeX/dx+1 
        if self.dimension >1:
            yc = self.sizeY/dy+1
        if self.dimension >2:
            zc = self.sizeZ/dz+1
        return [int(xc), int(yc), int(zc)]

    def getCellOffset(self, dx, dy, dz ):
        #TODO complete
        yc, zc = 1, 1
        xc = self.offsetX/dx 
        if self.dimension >1:
            yc = self.offsetY/dy
        if self.dimension >2:
            zc = self.offsetZ/dz
        return [int(xc), int(yc), int(zc)]
        
    def fillProperties(self, bdict):
        self.name = bdict["Name"]
        self.dimension = bdict["Dimension"]
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
            ("Dimension", self.dimension),
            ("Offset", offsetDict),
            ("Size", sizeDict),            
            ("DefaultEquation", self.defaultEquation),
            ("DefaultInitial", self.defaultInitial),
            ("BoundRegions", [bdict.getPropertiesDict(self.dimension) for bdict in  self.boundRegions]),
            ("InitialRegions", [idict.getPropertiesDict(self.dimension) for idict in  self.initialRegions])
        ])   
        return propDict