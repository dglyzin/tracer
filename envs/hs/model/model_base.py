'''
Created on Mar 19, 2015

@author: dglyzin


Model stores everything that user can provide.
It is created all empty
Interconnects are not created by default
Use add*(dict) to create * from existing dict
'''


from collections import OrderedDict
from pandas import DataFrame


# from domainmodel.criminal.parser import Parser
# from someFuncs import getRangesInClosedInterval

# from domainmodel.DerivHandler import DerivativeHandler
# from domainmodel.DelayHandler import DelayHandler
# generators
# from domainmodel.customOfficer import Reviewer
# from domainmodel.funcGenerator import FuncGenerator
# from domainmodel import compnode

XSTART = 0
XEND   = 1
YSTART = 2
YEND   = 3
ZSTART = 4
ZEND   = 5


class ModelBase(object):
    
    def __init__(self, net):
        self.net = net

        super(ModelBase, self).__init__()
        
        self.setSimpleValues()
        #self.connection = Connection()
        self.net.blocks = []
        self.net.interconnects = []
        self.net.equations = []
        self.net.params = []
        self.net.paramValues = []
        self.net.bounds = []
        self.net.initials = []
        self.net.compnodes = []
        self.net.plots = []
        self.net.results = []

    def setSimpleValues(self, projdict=[]):
        if projdict == []:
            self.projectName = "New project"

            self.net.solver.startTime = 0.0
            self.net.solver.finishTime = 1.0
            self.net.solver.timeStep = 0.05
            self.net.solver.saveInterval = 0.1
            self.net.solver.solverIndex = 0
            self.net.solver.solverAtol = 0.01
            self.net.solver.solverRtol = 0.01

            self.net.grid.gridStepX = 1.0
            self.net.grid.gridStepY = 1.0
            self.net.grid.gridStepZ = 1.0

            self.net.dimension = 1
            self.net.defaultParamsIndex = -1
        else:
            self.projectName = projdict["ProjectName"]

            self.net.solver.startTime = projdict["Solver"]["StartTime"]
            self.net.solver.finishTime = projdict["Solver"]["FinishTime"]
            self.net.solver.timeStep = projdict["Solver"]["TimeStep"]
            self.net.solver.saveInterval = projdict["Solver"]["SaveInterval"]
            self.net.solver.solverIndex = projdict["Solver"]["SolverIdx"]
            self.net.solver.solverAtol = projdict["Solver"]["AbsTolerance"]
            self.net.solver.solverRtol = projdict["Solver"]["RelTolerance"]
            
            self.net.dimension = projdict["Grid"]["Dimension"]

            self.net.grid.gridStepX = projdict["Grid"]["dx"]
            self.net.grid.gridStepY = projdict["Grid"]["dy"]
            self.net.grid.gridStepZ = projdict["Grid"]["dz"]
            
            self.net.params = projdict["EquationParams"]["Params"]
            self.net.paramValues = projdict["EquationParams"]["ParamValues"]
            if len(self.net.paramValues) == 1:
                self.net.defaultParamsIndex = 0
            elif len(self.net.paramValues) > 1:
                self.net.defaultParamsIndex = projdict["EquationParams"]["DefaultParamsIndex"]
            
    def clearAll(self):
        self.setSimpleValues()
        self.net.io.initSessionSettings()

        self.deleteAllBlocks()
        self.deleteAllInterconnects()
        self.deleteAllEquations()
        self.deleteAllBounds()
        self.deleteAllInitials()

    ## PRINT
    def show(self, outDict=None):
        '''
        DESCRIPTION:
        For print(model).
        '''
        out = ""
        '''
        if outDict is None:
            outDict = self.toDict()
            
        if type(outDict) == list:
            for l in outDict:
                out += self.__repr__(l) + "\n"
        elif type(outDict) == OrderedDict:
            out += str(DataFrame(outDict))
        
            for i, key in enumerate(outDict):
                out += ("\n"
                        + str(key) + " " + "\n"
                        + self.__repr__(outDict[key]))
        
        else:
            # in case of any other type (like int, ...):
            out = str(outDict)
        '''
        
        return(self.toDict())

    def to_frame(self):
        
        # ("Connection", self.connection.toDict()),
        print("ProjectName: %s" % self.projectName)
        print("\nSolver:")
        print(DataFrame([
            ("SolverIdx", self.net.solver.solverIndex),
            ("StartTime", self.net.solver.startTime),
            ("FinishTime", self.net.solver.finishTime),
            ("TimeStep", self.net.solver.timeStep),

            ("SaveInterval", self.net.solver.saveInterval),
            ("AbsTolerance", self.net.solver.solverAtol),
            ("RelTolerance", self.net.solver.solverRtol)]))

        print("\nGrid:")
        print(DataFrame([
            ("Dimension", self.net.dimension),
            ("dx", self.net.grid.gridStepX),
            ("dy", self.net.grid.gridStepY),
            ("dz", self.net.grid.gridStepZ)]))
        
        print("\nBlocks:")
        print(DataFrame([block.base.getPropertiesDict()
                         for block in self.net.blocks]))
        print("\nInterconnects:")
        print(DataFrame([ic.getPropertiesDict()
                         for ic in self.net.interconnects]))
        print("\nEquations:")
        print(DataFrame([equation.getPropertiesDict()
                         for equation in self.net.equations]))
        '''
        print("\nEquationParams:")
        print(DataFrame([
            ("Params", self.net.params),
            ("ParamValues", self.net.paramValues),
            ("DefaultParamsIndex", self.net.defaultParamsIndex)]))
        '''
        print("\nBounds:")
        print(DataFrame([bound.getPropertiesDict()
                         for bound in self.net.bounds]))
        print("\nInitials:")
        print(DataFrame([initial.getPropertiesDict()
                         for initial in self.net.initials]))
        print("\nHardware:")
        print(DataFrame([compnode.getPropertiesDict()
                         for compnode in self.net.compnodes]))
        print("\nMapping:")
        print("IsMapped: %s " % str(self.net.isMapped))
        print("BlockMapping")
        print(DataFrame(self.net.mapping))
        print("\nPlots:")
        print(DataFrame(self.net.plots))
        print("\nResults")
        print(DataFrame(self.net.results))
        
    def toDict(self):
        modelDict = OrderedDict([
            # ("Connection", self.connection.toDict()),
            ("ProjectName", self.projectName),
            ("Solver", OrderedDict([
                ("SolverIdx", self.net.solver.solverIndex),
                ("StartTime", self.net.solver.startTime),
                ("FinishTime", self.net.solver.finishTime),
                ("TimeStep", self.net.solver.timeStep),

                ("SaveInterval", self.net.solver.saveInterval),
                ("AbsTolerance", self.net.solver.solverAtol),
                ("RelTolerance", self.net.solver.solverRtol)])),

            ("Grid", OrderedDict([
                ("Dimension", self.net.dimension),
                ("dx", self.net.grid.gridStepX),
                ("dy", self.net.grid.gridStepY),
                ("dz", self.net.grid.gridStepZ)])),
            ("Blocks", [block.io.getPropertiesDict()
                        for block in self.net.blocks]),
            ("Interconnects", [ic.io.getPropertiesDict()
                               for ic in self.net.interconnects]),
            ("Equations", [equation.io.getPropertiesDict()
                           for equation in self.net.equations]),
            ("EquationParams", OrderedDict([
                ("Params", self.net.params),
                ("ParamValues", self.net.paramValues),
                ("DefaultParamsIndex", self.net.defaultParamsIndex)])),
            ("Bounds", [bound.getPropertiesDict()
                        for bound in self.net.bounds]),
            ("Initials", [initial.getPropertiesDict()
                          for initial in self.net.initials]),
            ("Hardware", [compnode.getPropertiesDict()
                          for compnode in self.net.compnodes]),
            ("Mapping", OrderedDict([("IsMapped", self.net.isMapped),
                                     ("BlockMapping", self.net.mapping)])),
            ("Plots", self.net.plots),
            ("Results", self.net.results)])
        return modelDict

    ### Blocks:
    def deleteBlock(self, index):
        del self.net.blocks[index]

    def deleteAllBlocks(self):
        self.net.blocks = []

    ###Interconnects
    def deleteInterconnect(self, index):
        del self.net.interconnects[index]

    def deleteAllInterconnects(self):
        self.net.interconnects = []

    ###Equations
    def deleteEquation(self, index):
        del self.net.equations[index]

    def deleteAllEquations(self):
        self.net.equations = []

    ###Bounds
    def deleteBound(self, index):
        del self.net.bounds[index]

    def deleteAllBounds(self):
        self.net.bounds = []

    ###Initials
    def deleteInitial(self, index):
        del self.net.initials[index]

    def deleteAllInitials(self):
        self.net.initials = []

    def getCellSize(self):
        return(len(self.net.equations[0].system))

    # TODO: getMaxDerivOrder
    def getHaloSize(self):
        order =  self.getMaxDerivOrder()
        return(order/2 + order%2)
                    
    def applyParams(self, paramSet):
        for param in paramSet:
            self.net.paramValues[0][param["Name"]] = param["Value"]
    
    # the following function is useful for json format updating
    def setSimpleValuesOld(self, projdict=[]):
        if projdict == []:
            self.projectName = "New project"

            self.net.solver.startTime = 0.0
            self.net.solver.finishTime = 1.0
            self.net.solver.timeStep = 0.05
            self.net.solver.saveInterval = 0.1
            self.net.solver.solverIndex = 0
            self.net.solver.soverAtol = 0.01
            self.net.solver.soverRtol = 0.01

            self.net.grid.gridStepX = 1.0
            self.net.grid.gridStepY = 1.0
            self.net.grid.gridStepZ = 1.0

            self.net.dimension = 1
            self.net.defaultParamsIndex = -1
        else:
            self.projectName = projdict["ProjectName"]

            self.net.solver.startTime = projdict["Solver"]["StartTime"]
            self.net.solver.finishTime = projdict["Solver"]["FinishTime"]
            self.net.solver.timeStep = projdict["Solver"]["TimeStep"]
            self.net.solver.saveInterval = projdict["Solver"]["SaveInterval"]
            self.net.solver.solverIndex = projdict["Solver"]["SolverIdx"]
            self.net.solver.solverAtol = projdict["Solver"]["AbsTolerance"]
            self.net.solver.solverRtol = projdict["Solver"]["RelTolerance"]
            
            try:
                self.net.dimension = projdict["Grid"]["Dimension"]
            except:
                self.net.dimension = projdict["Blocks"][0]["Dimension"]
            
            self.grid.gridStepX = projdict["Grid"]["dx"]
            self.grid.gridStepY = projdict["Grid"]["dy"]
            self.grid.gridStepZ = projdict["Grid"]["dz"]
            
            self.net.params = projdict["EquationParams"]["Params"]
            self.net.paramValues = projdict["EquationParams"]["ParamValues"]
            if len(self.net.paramValues) == 1:
                self.net.defaultParamsIndex = 0
            elif len(self.net.paramValues) > 1:
                self.net.defaultParamsIndex = projdict["EquationParams"]["DefaultParamsIndex"]
