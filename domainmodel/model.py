# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin


Model stores everything that user can provide.
It is created all empty 
Use addBlank* to create blocks, equations and bounds for editing (all members are initialized there (using constructor))
Interconnects are not created by default
Use add*(dict) to create * from existing dict
'''


import json
from collections import OrderedDict
from PyQt4.QtCore import QObject, pyqtSignal
import os
from block import Block 
from interconnect import Interconnect
from equation import Equation
from bound import Bound
from initial import Initial
from compnode import Compnode

XSTART = 0
XEND   = 1
YSTART = 2
YEND   = 3
ZSTART = 4
ZEND   = 5




class Model(QObject):  
    equationAdded = pyqtSignal(object)
    equationDeleted = pyqtSignal(object)
    equationChanged = pyqtSignal(object)
    allEquationsDeleted = pyqtSignal()
    equationNameChanged = pyqtSignal(object, object)
    
    boundAdded = pyqtSignal(object)
    boundDeleted = pyqtSignal(object)
    boundChanged = pyqtSignal(object)
    allBoundsDeleted = pyqtSignal()
    boundNameChanged = pyqtSignal(object, object)
    
    blockAdded = pyqtSignal(object)
    blockDeleted = pyqtSignal(object)
    blockChanged = pyqtSignal(object)
    allBlocksDeleted = pyqtSignal()
    
    interconnectAdded = pyqtSignal(object)
    interconnectDeleted = pyqtSignal(object)
    interconnectChanged = pyqtSignal(object)      
    allInterconnectsDeleted = pyqtSignal()
        
    initialAdded = pyqtSignal(object)
    initialDeleted = pyqtSignal(object)
    initialChanged = pyqtSignal(object)      
    allInitialsDeleted = pyqtSignal()
    initialNameChanged = pyqtSignal(object, object)

    compnodeAdded = pyqtSignal(object)
    compnodeDeleted = pyqtSignal(object)
    compnodeChanged = pyqtSignal(object)      
    allCompnodesDeleted = pyqtSignal()

    modelUpdated = pyqtSignal()    
    
    def __init__(self):
        super(Model, self).__init__()                
        self.initSessionSettings()
        self.setSimpleValues()
        self.blocks = []
        self.interconnects = []
        self.equations = []
        self.bounds = []
        self.initials = []
        self.compnodes = []
    
    
    def setSimpleValues(self, projdict=[]):
        if projdict == []:
            self.projectName = "New project"
            self.startTime = 0.0
            self.finishTime = 1.0
            self.timeStep = 0.05
            self.saveInterval = 0.1
            self.gridStepX = 1
            self.gridStepY = 1
            self.gridStepZ = 1
        else:
            self.projectName = projdict["ProjectName"]
            self.startTime = projdict["StartTime"]
            self.finishTime = projdict["FinishTime"]
            self.timeStep = projdict["TimeStep"]
            self.saveInterval = projdict["SaveInterval"]
            self.gridStepX = projdict["GridStep"]["x"]
            self.gridStepY = projdict["GridStep"]["y"]
            self.gridStepZ = projdict["GridStep"]["z"]
    
        
    def initSessionSettings(self):
        #SESSION SETTINGS
        #possibly should be separated
        self.workDirectory = os.getcwd()#""           #directory for computations
        self.projectFileAssigned = False  #
        self.projectFileName = ""         #path and file to the current json                
    
    def clearAll(self):
        self.setSimpleValues()        
        self.initSessionSettings()

        self.deleteAllBlocks()
        self.deleteAllInterconnects()
        self.deleteAllEquations()
        self.deleteAllBounds()
        self.deleteAllInitials()

        self.addBlankEquation()          #can't live without at least one equation
        self.addBlankBlock()             #and one block        
        self.addBlankInitial()           #and one initial value
        
        self.modelUpdated.emit()
        
  
    ##LOAD    
    def loadFromFile(self, fileName):      
        self.deleteAllBlocks()
        self.deleteAllInterconnects()
        self.deleteAllEquations()
        self.deleteAllBounds()
        self.deleteAllInitials()
               
        projectFile = open(fileName)
        projectDict = json.loads(projectFile.read())
        projectFile.close()

        self.setSimpleValues(projectDict)       
        for blockDict in projectDict["Blocks"]:            
            self.addBlock(blockDict)
        for icDict in projectDict["Interconnects"]:
            self.addInterconnect(icDict) 
        for equationDict in projectDict["Equations"]:            
            self.addEquation(equationDict)            
        for boundDict in projectDict["Bounds"]:            
            self.addBound(boundDict)            
        for initialDict in projectDict["Initials"]:
            self.addInitial(initialDict)            
        for compnodeDict in projectDict["Hardware"]:
            self.addCompnode(compnodeDict)           
                
        self.initSessionSettings()
        self.projectFileAssigned = True
        self.projectFile = fileName
        self.workDirectory = os.path.dirname(str(fileName))
        
        self.modelUpdated.emit()
        
        

    ##SAVE    
    def toDict(self):
        modelDict = OrderedDict([            
            ("ProjectName", self.projectName),
            ("StartTime", self.startTime),
            ("FinishTime", self.finishTime),
            ("TimeStep", self.timeStep),
            ("SaveInterval", self.saveInterval),
            ("GridStep", OrderedDict([
                            ("x", self.gridStepX),
                            ("y", self.gridStepY),
                            ("z", self.gridStepZ)
                         ]) ),
            
            ("Blocks", [block.getPropertiesDict() for block in self.blocks] ),
            ("Interconnects", [ic.getPropertiesDict() for ic in self.interconnects] ),            
            ("Equations", [equation.getPropertiesDict() for equation in self.equations] ),
            ("Bounds", [bound.getPropertiesDict() for bound in self.bounds] ),
            ("Initials", [initial.getPropertiesDict() for initial in self.initials]),
            ("Hardware", [compnode.getPropertiesDict() for compnode in self.compnodes]),
                        
        ])        
        return modelDict  
  
    def toJson(self):
        return json.dumps(self.toDict(),  sort_keys=False, indent = 4)
      
    def saveToFile(self, fileName):
        projectFile = open(fileName, "w")
        projectFile.write(self.toJson())
        projectFile.close()             
        
        if self.workDirectory != os.path.dirname(str(fileName)):
            self.initSessionSettings()
            self.workDirectory = os.path.dirname(str(fileName))        
        self.projectFileAssigned = True
        self.projectFile = fileName        
        
        

    def setWorkDirectory(self, folder):
        self.workDirectory = folder
        
    
       
    ###Blocks
    def addBlankBlock(self, dimension):        
        block = Block(u"Block {num}".format(num = len(self.blocks) + 1), dimension)
        self.blocks.append(block)
        self.blockAdded.emit(block)

    def fillBlockProperties(self, index, bdict):
        self.blocks[index].fillProperties(bdict)
        self.blockChanged.emit(index)
   
    def addBlock(self, bdict):
        index = len(self.blocks)
        self.addBlankBlock(bdict["Dimension"])
        self.fillBlockProperties(index, bdict)        
       
    def deleteBlock(self, index):
        del self.blocks[index]
        self.blockDeleted.emit(index)

    def deleteAllBlocks(self):
        self.blocks = []
        self.allBlocksDeleted.emit()
        
    def blockToJson(self, index):
        return self.blocks[index].toJson()
      
    ###Interconnects
    def addBlankInterconnect(self):        
        ic  = Interconnect(u"Connection {num}".format(num = len(self.interconnects) + 1))
        self.interconnects.append(ic)
        self.interconnectAdded.emit(ic)

    def fillInterconnectProperties(self, index, idict):
        self.interconnects[index].fillProperties(idict)
        self.interconnectChanged.emit(index)
   
    def addInterconnect(self, idict):
        index = len(self.interconnects)
        self.addBlankInterconnect()
        self.fillInterconnectProperties(index, idict)        
       
    def deleteInterconnect(self, index):
        del self.interconnects[index]
        self.interconnectDeleted.emit(index)

    def deleteAllInterconnects(self):
        self.interconnects = []
        self.allInterconnectsDeleted.emit()
        
    def interconnectToJson(self, index):
        return self.interconnects[index].toJson()       
      
       
       
    ###Equations
    def addBlankEquation(self):        
        equation = Equation(u"Equation {num}".format(num = len(self.equations) + 1))
        self.equations.append(equation)
        self.equationAdded.emit(equation)

    def addEquation(self, edict):
        index = len(self.equations)
        self.addBlankEquation()
        self.fillEquationProperties(index,edict)
        
    def fillEquationProperties(self, index, edict):
        self.equations[index].fillProperties(edict)
        self.equationChanged.emit(index)
    
    def deleteEquation(self, index):
        del self.equations[index]
        self.equationDeleted.emit(index)

    def deleteAllEquations(self):
        self.equations = []
        self.allEquationsDeleted.emit()
        
    def equationToJson(self, index):
        return self.equations[index].toJson()


    ###Bounds
    def addBlankBound(self):        
        bound = Bound(u"Bound {num}".format(num = len(self.bounds) + 1))
        self.bounds.append(bound)
        self.boundAdded.emit(bound)

    def addBound(self, bdict):
        index = len(self.bounds)
        self.addBlankBound()
        self.fillBoundProperties(index, bdict)
    
    def fillBoundProperties(self, index, bdict):
        self.bounds[index].fillProperties(bdict)
        self.boundChanged.emit(index)
   
    def deleteBound(self, index):
        del self.bounds[index]
        self.boundDeleted.emit(index)

    def deleteAllBounds(self):
        self.bounds = []
        self.allBoundsDeleted.emit()
            
    def boundToJson(self, index):
        return self.bounds[index].toJson()

    ###Initials
    def addBlankInitial(self):        
        initial = Initial(u"Initial {num}".format(num = len(self.initials) + 1))
        self.initials.append(initial)
        self.initialAdded.emit(initial)

    def addInitial(self, idict):
        index = len(self.initials)
        self.addBlankInitial()
        self.fillInitialProperties(index, idict)
    
    def fillInitialProperties(self, index, idict):
        self.initials[index].fillProperties(idict)
        self.initialChanged.emit(index)
   
    def deleteInitial(self, index):
        del self.initials[index]
        self.initialDeleted.emit(index)

    def deleteAllInitials(self):
        self.initials = []
        self.allInitialsDeleted.emit()
            
    def initialToJson(self, index):
        return self.initials[index].toJson()

    ####Computation nodes
    def addBlankCompnode(self):
        compnode = Compnode()
        self.compnodes.append(compnode)
        self.compnodeAdded.emit(compnode)       
        
    def addCompnode(self, cdict):
        index = len(self.compnodes)
        self.addBlankCompnode()
        self.fillCompnodeProperties(index,cdict) 
    
    def fillCompnodeProperties(self,index,cdict):
        self.compnodes[index].fillProperties(cdict)
        self.compnodeChanged.emit(index)
        
    def deleteCompnode(self, index):
        del self.compnodex[index]
        self.compnodeDeleted.emit(index)

    def deleteAllCompnodes(self):
        self.compnodes = []
        self.allCompnodesDeleted.emit()
            
    def compnodeToJson(self, index):
        return self.compnodes[index].toJson()

    def getDeviceCount(self):
        return sum([node.cpuCount+node.gpuCount for node in self.compnodes])         
