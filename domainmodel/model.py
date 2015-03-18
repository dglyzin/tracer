# -*- coding: utf-8 -*-

import json
from collections import OrderedDict
from PyQt4.QtCore import QObject, pyqtSignal
import os

'''
Model stores everything that user can provide.
It is created all empty 
Use addBlank* to create blocks, equations and bounds for editing (all members are initialized there (using constructor))
Interconnects are not created by default
Use add*(dict) to create * from existing dict
'''

XSTART = 0
XEND   = 1
YSTART = 2
YEND   = 3
ZSTART = 4
ZEND   = 5

class BoundRegion(object):
    def __init__(self, dict, dimension):
        self.boundNumber = dict["BoundNumber"]
        self.side = dict["Side"]
        if dimension>1:
            self.xfrom = dict["xfrom"]
            self.xto = dict["xto"]
            self.yfrom = dict["yfrom"]
            self.yto = dict["yto"]
        if dimension>2:
            self.zfrom = dict["zfrom"]
            self.zto = dict["zto"]
        
    
    def getPropertiesDict(self, dimension):
        propDict = OrderedDict([            
            ("BoundNumber", self.boundNumber),
            ("Side", self.side)
        ])   
        if dimension>1:
            propDict.update({"xfrom":self.xfrom})
            propDict.update({"xto":self.xto})
            propDict.update({"yfrom":self.yfrom})
            propDict.update({"yto":self.yto})
        if dimension>2:
            propDict.update({"zfrom":self.zfrom})
            propDict.update({"zto":self.zto})
        return propDict  


class InitialRegion(object):
    def __init__(self, dict, dimension):
        self.initialNumber = dict["InitialNumber"]        
        self.xfrom = dict["xfrom"]
        self.xto = dict["xto"]
        if dimension>1:            
            self.yfrom = dict["yfrom"]
            self.yto = dict["yto"]
        if dimension>2:
            self.zfrom = dict["zfrom"]
            self.zto = dict["zto"]
        
    
    def getPropertiesDict(self, dimension):
        propDict = OrderedDict([            
            ("InitialNumber", self.initialNumber),
            ("xfrom", self.xfrom),
            ("xto", self.xto)
        ])   
        if dimension>1:            
            propDict.update({"yfrom":self.yfrom})
            propDict.update({"yto":self.yto})
        if dimension>2:
            propDict.update({"zfrom":self.zfrom})
            propDict.update({"zto":self.zto})
        return propDict  


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
        
        
    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.dimension = dict["Dimension"]
        self.offsetX = dict["Offset"]["x"]
        self.sizeX = dict["Size"]["x"]        
        if self.dimension > 1:
            self.offsetY = dict["Offset"]["y"]
            self.sizeY = dict["Size"]["y"]            
        if self.dimension > 2:
            self.offsetZ = dict["Offset"]["z"]
            self.sizeZ = dict["Size"]["z"]            
        
        self.defaultEquation = dict["DefaultEquation"]
        self.defaultInitial = dict["DefaultInitial"]
        
        self.boundRegions = []
        for boundDict in dict["BoundRegions"]:
            self.boundRegions.append(BoundRegion(boundDict,self.dimension))
        for initDict in dict["InitialRegions"]:
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

class Interconnect(object):
    def __init__(self, name):
        self.name = name
        self.block1 = 0
        self.block2 = 0
        self.block1Side = 0
        self.block2Side = 1

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.block1 = dict["Block1"]
        self.block2 = dict["Block2"]
        self.block1Side = dict["Block1Side"]
        self.block2Side = dict["Block2Side"]
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Block1", self.block1),
            ("Block2", self.block2),
            ("Block1Side", self.block1Side),
            ("Block2Side", self.block2Side)       
        ])   
        return propDict  
      
class Equation(object):
    def __init__(self, name):
        self.name = name
        self.vars = "x"
        self.system = ["U'=1"]

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.vars = dict["Vars"]
        self.system = dict["System"]
        self.params = dict["Params"]
        self.paramValues = dict["ParamValues"]
   
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Vars", self.vars),
            ("System", self.system),
            ("Params", self.params),
            ("ParamValues", self.paramValues)
        ])   
        return propDict  

class Bound(object):
    def __init__(self, name):
        self.name = name
        self.btype = 0
        self.values = ["0"]

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.btype = dict["Type"]
        self.values = dict["Values"]        
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Type", self.btype),
            ("Values", self.values)            
        ])   
        return propDict  

class Initial(object):
    def __init__(self, name):
        self.name = name
        self.values = ["0"]

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.values = dict["Values"]        

    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),            
            ("Values", self.values)            
        ])   
        return propDict  


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
            ("Initials", [initial.getPropertiesDict() for initial in self.initials])            
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

    def fillBlockProperties(self, index, dict):
        self.blocks[index].fillProperties(dict)
        self.blockChanged.emit(index)
   
    def addBlock(self, dict):
        index = len(self.blocks)
        self.addBlankBlock(dict["Dimension"])
        self.fillBlockProperties(index, dict)        
       
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

    def fillInterconnectProperties(self, index, dict):
        self.interconnects[index].fillProperties(dict)
        self.interconnectChanged.emit(index)
   
    def addInterconnect(self, dict):
        index = len(self.interconnects)
        self.addBlankInterconnect()
        self.fillInterconnectProperties(index, dict)        
       
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
        equation = Equation(u"Грунт {num}".format(num = len(self.equations) + 1))
        self.equations.append(equation)
        self.equationAdded.emit(equation)

    def addEquation(self, dict):
        index = len(self.equations)
        self.addBlankEquation()
        self.fillEquationProperties(index,dict)
        
    def fillEquationProperties(self, index,dict):
        self.equations[index].fillProperties(dict)
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

    def addBound(self, dict):
        index = len(self.bounds)
        self.addBlankBound()
        self.fillBoundProperties(index, dict)
    
    def fillBoundProperties(self, index, dict):
        self.bounds[index].fillProperties(dict)
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

    def addInitial(self, dict):
        index = len(self.initials)
        self.addBlankInitial()
        self.fillInitialProperties(index, dict)
    
    def fillInitialProperties(self, index, dict):
        self.initials[index].fillProperties(dict)
        self.initialChanged.emit(index)
   
    def deleteInitial(self, index):
        del self.initials[index]
        self.initialDeleted.emit(index)

    def deleteAllInitials(self):
        self.initials = []
        self.allInitialsDeleted.emit()
            
    def initialToJson(self, index):
        return self.initials[index].toJson()
   