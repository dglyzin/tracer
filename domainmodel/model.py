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
import os

import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.block import Block
    from domainmodel.interconnect import Interconnect
    from domainmodel.equation import Equation
    from domainmodel.bound import Bound
    from domainmodel.initial import Initial
    from domainmodel.compnode import Compnode
    from domainmodel.criminal.parser import Parser

    from domainmodel.DerivHandler import DerivativeHandler
    from domainmodel.DelayHandler import DelayHandler
    # generators
    from domainmodel.customOfficer import Reviewer
    from domainmodel.funcGenerator import FuncGenerator
    from domainmodel.someFuncs import getRangesInClosedInterval
    from domainmodel import compnode

else:
    from block import Block
    from interconnect import Interconnect
    from equation import Equation
    from bound import Bound
    from initial import Initial
    from compnode import Compnode
    from criminal.parser import Parser

    from DerivHandler import DerivativeHandler
    from DelayHandler import DelayHandler
    # generators
    from customOfficer import Reviewer
    from funcGenerator import FuncGenerator
    from someFuncs import getRangesInClosedInterval
    from domainmodel import compnode

#from libGenerateC import generateCfromDict


XSTART = 0
XEND   = 1
YSTART = 2
YEND   = 3
ZSTART = 4
ZEND   = 5



class Model(object):
    
    def __init__(self):
        super(Model, self).__init__()
        self.initSessionSettings()
        self.setSimpleValues()
        #self.connection = Connection()
        self.blocks = []
        self.interconnects = []
        self.equations = []
        self.params = []
        self.paramValues = []
        self.bounds = []
        self.initials = []
        self.compnodes = []
        self.plots = []
        self.results = []

    #the following function is useful for json format updating
    
    def setSimpleValuesOld(self, projdict=[]):
        if projdict == []:
            self.projectName = "New project"
            self.startTime = 0.0
            self.finishTime = 1.0
            self.timeStep = 0.05
            self.saveInterval = 0.1
            self.solverIndex = 0
            self.soverAtol = 0.01
            self.soverRtol = 0.01
            self.gridStepX = 1.0
            self.gridStepY = 1.0
            self.gridStepZ = 1.0
            self.dimension = 1
            self.defaultParamsIndex = -1
        else:
            self.projectName = projdict["ProjectName"]
            self.startTime = projdict["Solver"]["StartTime"]
            self.finishTime = projdict["Solver"]["FinishTime"]
            self.timeStep = projdict["Solver"]["TimeStep"]
            self.saveInterval = projdict["Solver"]["SaveInterval"]
            self.solverIndex = projdict["Solver"]["SolverIdx"]
            self.solverAtol = projdict["Solver"]["AbsTolerance"]
            self.solverRtol = projdict["Solver"]["RelTolerance"]
            
            try:
                self.dimension = projdict["Grid"]["Dimension"]
            except:
                self.dimension = projdict["Blocks"][0]["Dimension"]
            
            self.gridStepX = projdict["Grid"]["dx"]
            self.gridStepY = projdict["Grid"]["dy"]
            self.gridStepZ = projdict["Grid"]["dz"]
            
            
            self.params = projdict["EquationParams"]["Params"]
            self.paramValues = projdict["EquationParams"]["ParamValues"]
            if len(self.paramValues) == 1:
                self.defaultParamsIndex = 0
            elif len(self.paramValues) > 1:
                self.defaultParamsIndex = projdict["EquationParams"]["DefaultParamsIndex"]
        

    def setSimpleValues(self, projdict=[]):
        if projdict == []:
            self.projectName = "New project"
            self.startTime = 0.0
            self.finishTime = 1.0
            self.timeStep = 0.05
            self.saveInterval = 0.1
            self.solverIndex = 0
            self.soverAtol = 0.01
            self.soverRtol = 0.01
            self.gridStepX = 1.0
            self.gridStepY = 1.0
            self.gridStepZ = 1.0
            self.dimension = 1
            self.defaultParamsIndex = -1
        else:
            self.projectName = projdict["ProjectName"]
            self.startTime = projdict["Solver"]["StartTime"]
            self.finishTime = projdict["Solver"]["FinishTime"]
            self.timeStep = projdict["Solver"]["TimeStep"]
            self.saveInterval = projdict["Solver"]["SaveInterval"]
            self.solverIndex = projdict["Solver"]["SolverIdx"]
            self.solverAtol = projdict["Solver"]["AbsTolerance"]
            self.solverRtol = projdict["Solver"]["RelTolerance"]
            
            self.dimension = projdict["Grid"]["Dimension"]
            self.gridStepX = projdict["Grid"]["dx"]
            self.gridStepY = projdict["Grid"]["dy"]
            self.gridStepZ = projdict["Grid"]["dz"]
            
            
            self.params = projdict["EquationParams"]["Params"]
            self.paramValues = projdict["EquationParams"]["ParamValues"]
            if len(self.paramValues) == 1:
                self.defaultParamsIndex = 0
            elif len(self.paramValues) > 1:
                self.defaultParamsIndex = projdict["EquationParams"]["DefaultParamsIndex"]
            


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


    ##LOAD
    #the following function is useful for json format updating
    
    def loadFromFileOld(self, fileName):
        self.deleteAllBlocks()
        self.deleteAllInterconnects()
        self.deleteAllEquations()
        self.deleteAllBounds()
        self.deleteAllInitials()

        projectFile = open(fileName)
        projectDict = json.loads(projectFile.read())
        projectFile.close()

        #self.connection.fromDict(projectDict["Connection"])

        self.setSimpleValuesOld(projectDict)
        for blockDict in projectDict["Blocks"]:
            self.addBlock(blockDict, self.dimension)
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

        self.isMapped = projectDict["Mapping"]["IsMapped"]
        self.mapping = [OrderedDict([("NodeIdx", block["NodeIdx"]),
                                     ("DeviceType", block["DeviceType"]),
                                     ("DeviceIdx", block["DeviceIdx"])
                                     ])                                   
                                     for block in projectDict["Mapping"]["BlockMapping"] ]
       
        try:
            self.plots = [ OrderedDict([("Title", plot["Title"]),
                                    ("Period", plot["Period"]),
                                    ("Value", plot["Value"])
                                    ]
                                   )
                 for plot in projectDict["Plots"] ]
        except:        
            self.plots = [ ]

        try:
            self.results = [ OrderedDict([("Name", result["Name"]),
                                    ("Period", result["Period"]),
                                    ("Value", result["Value"])
                                    ]
                                   )
                 for result in projectDict["Results"] ]
        except:        
            self.results = [ ]
        

        
        self.initSessionSettings()
        self.projectFileAssigned = True
        self.projectFile = fileName
        self.workDirectory = os.path.dirname(str(fileName))
    
        
    def loadFromFile(self, fileName):
        self.deleteAllBlocks()
        self.deleteAllInterconnects()
        self.deleteAllEquations()
        self.deleteAllBounds()
        self.deleteAllInitials()

        projectFile = open(fileName)
        projectDict = json.loads(projectFile.read())
        projectFile.close()

        #self.connection.fromDict(projectDict["Connection"])

        self.setSimpleValues(projectDict)
        for blockDict in projectDict["Blocks"]:
            self.addBlock(blockDict, self.dimension)
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

        self.isMapped = projectDict["Mapping"]["IsMapped"]
        self.mapping = [OrderedDict([("NodeIdx", block["NodeIdx"]),
                                     ("DeviceType", block["DeviceType"]),
                                     ("DeviceIdx", block["DeviceIdx"])
                                     ])                                   
                                     for block in projectDict["Mapping"]["BlockMapping"] ]
        try:
           
            self.plots = [OrderedDict([("Title", plot["Title"]),
                                       ("Period", plot["Period"]),
                                       ("Value", plot["Value"])])
                          for plot in projectDict["Plots"]]
        except:
            self.plots = []

        try:
            self.results = [OrderedDict([("Name", result["Name"]),
                                         ("Period", result["Period"]),
                                         ("Value", result["Value"])])
                            for result in projectDict["Results"]]
        except:
            self.results = []

        self.initSessionSettings()
        self.projectFileAssigned = True
        self.projectFile = fileName
        self.workDirectory = os.path.dirname(str(fileName))

        parser = Parser()
        if self.dimension == 1:
            parser.params.dim = '1D'
        else:
            parser.params.dim = '2D'
        cellSize = 1
        parser.params.shape = [cellSize/float(self.gridStepX),
                               cellSize/float(self.gridStepY),
                               cellSize/float(self.gridStepZ)]
        for block in self.blocks:
            block.parser = parser


    ## PRINT
    def __repr__(self):
        '''
        DESCRIPTION:
        For print(model).
        '''
        out = ""
        outDict = self.toDict()
        # lists = ('Blocks', 'Interconnects', 'Equations', 'Bounds')
        for key in outDict:
            outVal = ""
            if type(outDict[key]) == list:
                for i in range(len(outDict[key])):
                    outVal = (outVal
                              + "\n\n"
                              + str(key)[:-1] + " " + str(i)
                              + "\n"
                              + str(outDict[key][i]))
            else:
                outVal = str(outDict[key])

            out = (out
                   + str(key)
                   + '\n ############## \n'
                   + outVal
                   + '\n\n')
        return(out)

    ##SAVE
    def toDict(self):        
        modelDict = OrderedDict([
            #("Connection", self.connection.toDict()),
            ("ProjectName", self.projectName),
            ("Solver", OrderedDict([
                            ("SolverIdx", self.solverIndex),
                            ("StartTime", self.startTime),
                            ("FinishTime", self.finishTime),
                            ("TimeStep", self.timeStep),
                            ("SaveInterval", self.saveInterval),                            
                            ("AbsTolerance", self.solverAtol),
                            ("RelTolerance", self.solverRtol),                                                    
                        ]) ),
            ("Grid", OrderedDict([
                            ("Dimension", self.dimension),
                            ("dx", self.gridStepX),
                            ("dy", self.gridStepY),
                            ("dz", self.gridStepZ)                            
                        ]) ),            
            ("Blocks", [block.getPropertiesDict() for block in self.blocks] ),
            ("Interconnects", [ic.getPropertiesDict() for ic in self.interconnects] ),
            ("Equations", [equation.getPropertiesDict() for equation in self.equations] ),
            ("EquationParams", OrderedDict([                            
                            ("Params", self.params),
                            ("ParamValues", self.paramValues),
                            ("DefaultParamsIndex", self.defaultParamsIndex)
                        ]) ),
            
            ("Bounds", [bound.getPropertiesDict() for bound in self.bounds] ),
            ("Initials", [initial.getPropertiesDict() for initial in self.initials]),
            ("Hardware", [compnode.getPropertiesDict() for compnode in self.compnodes]),
            ("Mapping", OrderedDict ([("IsMapped", self.isMapped),
                                      ("BlockMapping", self.mapping) 
                                    ]) ),
            ("Plots", self.plots),
            ("Results", self.results),
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
    def addBlankBlock(self):
        block = Block(u"Block {num}".format(num = len(self.blocks) + 1), self.dimension)
        self.blocks.append(block)
        

    def fillBlockProperties(self, index, bdict):
        self.blocks[index].fillProperties(bdict)
        

    def addBlock(self, bdict, dimension):
        index = len(self.blocks)
        self.addBlankBlock()
        self.fillBlockProperties(index, bdict)

    def deleteBlock(self, index):
        del self.blocks[index]
        

    def deleteAllBlocks(self):
        self.blocks = []
        

    def blockToJson(self, index):
        return self.blocks[index].toJson()

    ###Interconnects
    def addBlankInterconnect(self):
        ic  = Interconnect(u"Connection {num}".format(num = len(self.interconnects) + 1))
        self.interconnects.append(ic)

    def fillInterconnectProperties(self, index, idict):
        self.interconnects[index].fillProperties(idict)

    def addInterconnect(self, idict):
        index = len(self.interconnects)
        self.addBlankInterconnect()
        self.fillInterconnectProperties(index, idict)

    def deleteInterconnect(self, index):
        del self.interconnects[index]

    def deleteAllInterconnects(self):
        self.interconnects = []

    def interconnectToJson(self, index):
        return self.interconnects[index].toJson()



    ###Equations
    def addBlankEquation(self):
        equation = Equation(u"Equation {num}".format(num = len(self.equations) + 1))
        self.equations.append(equation)
        
    def addEquation(self, edict):
        index = len(self.equations)
        self.addBlankEquation()
        self.fillEquationProperties(index,edict)

    def fillEquationProperties(self, index, edict):
        self.equations[index].fillProperties(edict)

    def deleteEquation(self, index):
        del self.equations[index]

    def deleteAllEquations(self):
        self.equations = []

    def equationToJson(self, index):
        return self.equations[index].toJson()


    ###Bounds
    def addBlankBound(self):
        bound = Bound(u"Bound {num}".format(num = len(self.bounds) + 1))
        self.bounds.append(bound)

    def addBound(self, bdict):
        index = len(self.bounds)
        self.addBlankBound()
        self.fillBoundProperties(index, bdict)

    def fillBoundProperties(self, index, bdict):
        self.bounds[index].fillProperties(bdict)

    def deleteBound(self, index):
        del self.bounds[index]

    def deleteAllBounds(self):
        self.bounds = []

    def boundToJson(self, index):
        return self.bounds[index].toJson()

    ###Initials
    def addBlankInitial(self):
        initial = Initial(u"Initial {num}".format(num = len(self.initials) + 1))
        self.initials.append(initial)

    def addInitial(self, idict):
        index = len(self.initials)
        self.addBlankInitial()
        self.fillInitialProperties(index, idict)

    def fillInitialProperties(self, index, idict):
        self.initials[index].fillProperties(idict)

    def deleteInitial(self, index):
        del self.initials[index]

    def deleteAllInitials(self):
        self.initials = []

    def initialToJson(self, index):
        return self.initials[index].toJson()

    ####Computation nodes
    def addBlankCompnode(self):
        compnode = Compnode()
        self.compnodes.append(compnode)

    def addCompnode(self, cdict):
        index = len(self.compnodes)
        self.addBlankCompnode()
        self.fillCompnodeProperties(index,cdict)

    def fillCompnodeProperties(self,index,cdict):
        self.compnodes[index].fillProperties(cdict)

    def deleteCompnode(self, index):
        del self.compnodex[index]

    def deleteAllCompnodes(self):
        self.compnodes = []

    def compnodeToJson(self, index):
        return self.compnodes[index].toJson()

    def getDeviceCount(self):
        return sum([node.cpuCount+node.gpuCount for node in self.compnodes])

    def getNodeCount(self):
        return len(self.compnodes)
    
    def getNodeSpec(self):
        '''
        returns parameter string to slurm:
        -w cnodex cnodey ...
        if no "any" node is present in json
        and empty string otherwise
        '''
        paramLine = "-w"
        for node in self.compnodes:            
            if node.name == "any":
                return ""
            else:
                paramLine = paramLine + "," + node.name
        return paramLine

    def getCellSize(self):
        return len(self.equations[0].system)

    def getHaloSize(self):
        order =  self.getMaxDerivOrder()
        return order/2 + order%2

    def getMaxDerivOrder(self):
        d = DerivativeHandler()
        return d.orderOfSystem(self.equations[0].system,self.params, self.equations[0].vars)
        
    def determineDelay(self):
        d = DelayHandler()
        return d.determineDelay(self.equations[0].system,self.params, self.equations[0].vars)

    def createCPPandGetFunctionMaps(self, cppFileName, preprocessorFolder, nocppgen):
        #generator1
        # try:
        gridStep = [self.gridStepX, self.gridStepY, self.gridStepZ]
        reviewer = Reviewer(self.equations, self.blocks, self.initials,
                            self.bounds, gridStep, self.params,
                            self.paramValues, self.defaultParamsIndex)
        reviewer.ReviewInput()
        haloSize = self.getHaloSize()
        mDO = self.getMaxDerivOrder()
        delay_lst = []  # self.determineDelay()
        
        gen = FuncGenerator(delay_lst, mDO, haloSize, self.equations,
                            self.blocks, self.initials, self.bounds,
                            self.interconnects, gridStep, self.params,
                            self.paramValues, self.defaultParamsIndex,
                            preprocessorFolder)
        outputStr, functionMaps = gen.generateAllFunctions()
        # except Exception as ex:
        #    print("###")
        #    print(ex)
        # else:
        if not nocppgen:
            f = open(cppFileName,'w')
            f.write(outputStr)
            f.close()
        return (functionMaps, gen.delays)
        #generator2
        #generateCfromDict(self.toDict(),cppFileName)
        
        
    def getXrange(self, block, xfrom, xto):
        #xfrom -= block.offsetX
        #xto -= block.offsetX
        fromIdx, toIdx = getRangesInClosedInterval([xfrom, xto, self.gridStepX])
        #[xc, _, _ ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        #if fromIdx == 0: fromIdx = 1
        #if toIdx == xc: toIdx = xc-1
        return fromIdx, toIdx
    
    def getYrange(self, block, yfrom, yto):
        #yfrom -= block.offsetY
        #yto -= block.offsetY
        fromIdx, toIdx = getRangesInClosedInterval([yfrom, yto, self.gridStepY])
        #[_, yc, _ ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        #if fromIdx == 0: fromIdx = 1
        #if toIdx == yc: toIdx = yc-1
        return fromIdx, toIdx
    
    def getZrange(self, block, zfrom, zto):
        #zfrom -= block.offsetZ
        #zto -= block.offsetZ
        fromIdx, toIdx = getRangesInClosedInterval([zfrom, zto, self.gridStepZ])
        #[_, _, zc ] = block.getCellCount(self.gridStepX,self.gridStepY,self.gridStepZ)
        #if fromIdx == 0: fromIdx = 1
        #if toIdx == zc: toIdx = zc-1
        return fromIdx, toIdx
    
    def getDeviceStateSize(self, nodeIdx, deviceType, deviceIdx):
        '''
        counts state sizes for every block that is scheduled to a given node and a given device
        '''
        devStateSize = 0
        for (blockIdx, block) in enumerate(self.blocks):
            mapping = self.mapping[blockIdx]
            if (nodeIdx == mapping["NodeIdx"]) and (deviceType == mapping["DeviceType"]) and (deviceIdx == mapping["DeviceIdx"]):
                cellCount = block.getCellCount(self.gridStepX, self.gridStepY, self.gridStepZ)                
                devStateSize += cellCount[0]*cellCount[1]*cellCount[2]*self.getCellSize()
        return devStateSize
    
    def getMaxStatesCount(self):
        '''
        returns maximum number of states that can be 
        stored in memory by ANY computing device
        result = min_{for every computing device D} 
                     (D.memory/sum_{for every block B inside D} (B.total) )
        '''
        minCapacity = 0
        for nodeIdx, node in enumerate(self.compnodes):
            for cpuIdx in range(node.cpuCount):
                memorySize = node.cpuMemory[cpuIdx]
                devStateSize = self.getDeviceStateSize(nodeIdx, "cpu", cpuIdx)
                if devStateSize > 0:
                    capacity = int(memorySize * 1024 * 1024 * 1024/(8 *  devStateSize) )    
                    if (minCapacity == 0) or (capacity<minCapacity):
                        minCapacity = capacity
                else:
                    capacity = "infinity"
                print("For node {} {}{} memory is {}GB, total state size is {} elems, capacity={}.".format(node.name, "cpu", cpuIdx, memorySize, devStateSize, capacity))                 
            for gpuIdx in range(node.gpuCount):
                memorySize = node.gpuMemory[gpuIdx]
                devStateSize = self.getDeviceStateSize(nodeIdx, "gpu", gpuIdx)
                if devStateSize > 0:
                    capacity = int(memorySize * 1024 * 1024 * 1024/(8 * devStateSize ) )    
                    if (minCapacity == 0) or (capacity<minCapacity):
                        minCapacity = capacity
                else: 
                    capacity = "infinity"
                print("For node {} {}{} memory is {}GB, total state size is {} elems, capacity={}.".format(node.name, "gpu", gpuIdx, memorySize, devStateSize, capacity))              
                    
        return minCapacity #like 100*100*100 000 elements = 8GB < 64GB
            
    
    def applyParams(self,paramSet):
        for param in paramSet:
            self.paramValues[0][param["Name"]] = param["Value"]
    
    
