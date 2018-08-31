import os
import json

from envs.hs.block.block_main import BlockNet as Block
from envs.hs.block.block_size import BlockSize
from envs.hs.interconnect.ic_main import icMain as Interconnect
from math_space.common.env.system.sys_main import sysNet as System
from math_space.pde.bound import Bound
from math_space.pde.initial import Initial
from envs.hs.model.compnode import Compnode

from collections import OrderedDict


class ModelIO():
   
    def __init__(self, net):
        self.net = net
        self.initSessionSettings()

    def initSessionSettings(self):

        '''SESSION SETTINGS
        possibly should be separated'''

        # directory for computations:
        self.workDirectory = os.getcwd()

        self.projectFileAssigned = False
        
        # path and file to the current json
        self.projectFileName = ""

    def setWorkDirectory(self, folder):
        self.workDirectory = folder
        
    def loadFromFile(self, project_folder=('problems/1dTests/'
                                           + 'test1d_two_blocks0')):

        '''project_folder is relative path to project folder where
        .json file located (including problems folder).

        Ex: problems/1dTests/test1d_two_blocks0
           for
              problems/1dTests/test1d_two_blocks0/test1d_two_blocks0.json
           '''

        # FOR pathes:
        if 'problems' not in project_folder:
            raise(BaseException('path to folder with json must begin from'
                                + ' problems folder \n'
                                + ' like problems/1dTests/test1d_two_blocks0'))
        elif len(project_folder.split('.')) == 2:
            raise(BaseException('project_folder is name of folder in with'
                                + ' json file contained'
                                + ' like problems/1dTests/test1d_two_blocks0'))
        elif (project_folder[0] == '/'):
            raise(BaseException('project_folder is name of folder in with \n'
                                + ' json file contained, relative to '
                                + 'hybriddomain folder \n'
                                + ' like problems/1dTests/test1d_two_blocks0'))
        
        self.net.project_path = project_folder.replace('problems/', "")
        self.net.project_name = os.path.basename(self.net.project_path)

        # json file:
        fileName = [f for f in os.listdir(project_folder)
                    if ('.json' in f) and (r'.json~' not in f)][0]
        fileName = os.path.join(project_folder, fileName)
        # END FOR

        self.net.base.deleteAllBlocks()
        self.net.base.deleteAllInterconnects()
        self.net.base.deleteAllEquations()
        self.net.base.deleteAllBounds()
        self.net.base.deleteAllInitials()

        projectFile = open(fileName)
        projectDict = json.loads(projectFile.read())
        projectFile.close()

        # self.connection.fromDict(projectDict["Connection"])

        self.net.base.setSimpleValues(projectDict)
        for blockDict in projectDict["Blocks"]:
            # self.blocks.append(Block(blockDict))
            self.add_block_io(blockDict, self.net.dimension)
        for icDict in projectDict["Interconnects"]:
            self.add_interconnect_io(icDict)
        for equationDict in projectDict["Equations"]:
            self.add_equation_io(equationDict)
        for boundDict in projectDict["Bounds"]:
            self.add_bound_io(boundDict)
        for initialDict in projectDict["Initials"]:
            self.add_initial_io(initialDict)
        for compnodeDict in projectDict["Hardware"]:
            self.add_compnode_io(compnodeDict)

        self.net.isMapped = projectDict["Mapping"]["IsMapped"]
        
        self.net.mapping = [OrderedDict([("NodeIdx", block["NodeIdx"]),
                                         ("DeviceType", block["DeviceType"]),
                                         ("DeviceIdx", block["DeviceIdx"])])
                            for block in projectDict["Mapping"]["BlockMapping"]]
        try:
           
            self.net.plots = [OrderedDict([("Title", plot["Title"]),
                                           ("Period", plot["Period"]),
                                           ("Value", plot["Value"])])
                              for plot in projectDict["Plots"]]
        except:
            self.net.plots = []

        try:
            self.net.results = [OrderedDict([("Name", result["Name"]),
                                             ("Period", result["Period"]),
                                             ("Value", result["Value"])])
                                for result in projectDict["Results"]]
        except:
            self.net.results = []

        self.initSessionSettings()
        self.projectFileAssigned = True
        self.projectFile = fileName
        self.workDirectory = os.path.dirname(str(fileName))

        '''
        # parser = Parser()
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
        '''

    # the following function is useful for json format updating
    def loadFromFileOld(self, fileName):
        self.net.base.deleteAllBlocks()
        self.net.base.deleteAllInterconnects()
        self.net.base.deleteAllEquations()
        self.net.base.deleteAllBounds()
        self.net.base.deleteAllInitials()

        projectFile = open(fileName)
        projectDict = json.loads(projectFile.read())
        projectFile.close()

        #self.connection.fromDict(projectDict["Connection"])

        self.net.base.setSimpleValuesOld(projectDict)
        for blockDict in projectDict["Blocks"]:
            self.add_block_io(blockDict, self.dimension)
        for icDict in projectDict["Interconnects"]:
            self.add_interconnect_io(icDict)
        for equationDict in projectDict["Equations"]:
            self.add_equation_io(equationDict)
        for boundDict in projectDict["Bounds"]:
            self.add_bound_io(boundDict)
        for initialDict in projectDict["Initials"]:
            self.add_initial_io(initialDict)
        for compnodeDict in projectDict["Hardware"]:
            self.add_compnode_io(compnodeDict)

        self.net.isMapped = projectDict["Mapping"]["IsMapped"]
        self.net.mapping = [OrderedDict([("NodeIdx", block["NodeIdx"]),
                                         ("DeviceType", block["DeviceType"]),
                                         ("DeviceIdx", block["DeviceIdx"])])
                            for block in projectDict["Mapping"]["BlockMapping"]]
       
        try:
            self.net.plots = [OrderedDict([("Title", plot["Title"]),
                                           ("Period", plot["Period"]),
                                           ("Value", plot["Value"])])
                              for plot in projectDict["Plots"]]
        except:
            self.net.plots = []
        try:
            self.net.results = [OrderedDict([("Name", result["Name"]),
                                             ("Period", result["Period"]),
                                             ("Value", result["Value"])])
                                for result in projectDict["Results"]]
        except:
            self.net.results = []

        self.initSessionSettings()
        self.projectFileAssigned = True
        self.projectFile = fileName
        self.workDirectory = os.path.dirname(str(fileName))

    # SAVE
    def toJson(self):
        return json.dumps(self.net.base.toDict(), sort_keys=False, indent=4)

    def saveToFile(self, fileName):
        projectFile = open(fileName, "w")
        projectFile.write(self.toJson())
        projectFile.close()

        if self.workDirectory != os.path.dirname(str(fileName)):
            self.initSessionSettings()
            self.workDirectory = os.path.dirname(str(fileName))
        self.projectFileAssigned = True
        self.projectFile = fileName

    def add_block_io(self, bdict, dimension):
        name = u"Block {num}".format(num=len(self.net.blocks) + 1)
        size = BlockSize(None)
        size.set_default(self.net.dimension)
        index = len(self.net.blocks)
        block = Block(name, index, size)
        block.io.fillProperties(bdict)
        self.net.editor.add(block, self.net.blocks)

    def block_to_json(self, index):
        return self.net.blocks[index].toJson()

    def add_interconnect_io(self, idict):

        name = u"Connection {num}".format(num=len(self.net.interconnects) + 1)
        ic = Interconnect(name, self.net)
        ic.io.fillProperties(idict)
        self.net.editor.add(ic, self.net.interconnects)
            
    def interconnect_to_json(self, index):
        return self.net.interconnects[index].io.toJson()

    def add_equation_io(self, edict):
        name = u"Equation {num}".format(num=len(self.net.equations) + 1)
        equation = System(name)
        equation.io.fillProperties(edict)
        self.net.editor.add(equation, self.net.equations)

    def equation_to_json(self, index):
        return self.net.equations[index].toJson()

    def add_bound_io(self, bdict):
        
        bound = Bound(u"Bound {num}".format(num=len(self.net.bounds) + 1))
        bound.fillProperties(bdict)
        self.net.editor.add(bound, self.net.bounds)

    def bound_to_json(self, index):
        return self.net.bounds[index].toJson()

    def add_initial_io(self, idict):
        name = u"Initial {num}".format(num=len(self.net.initials)+1)
        initial = Initial(name)
        initial.fillProperties(idict)
        self.net.editor.add(initial, self.net.initials)

    def initial_to_json(self, index):
        return self.net.initials[index].toJson()

    def add_compnode_io(self, cdict):
        compnode = Compnode()
        compnode.fillProperties(cdict)
        self.net.editor.add(compnode, self.net.compnodes)

    def compnode_to_json(self, index):
        return self.net.compnodes[index].toJson()
