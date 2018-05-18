from math_space.pde.regions import EquationRegion
from math_space.pde.regions import BoundRegion
from math_space.pde.regions import InitialRegion

from collections import OrderedDict


class BlockIO():

    def __init__(self, net):
        self.net = net

    def fillProperties(self, bdict):
        self.net.base.name = bdict["Name"]
        self.net.size.offsetX = bdict["Offset"]["x"]
        self.net.size.sizeX = bdict["Size"]["x"]
        if self.net.size.dimension > 1:
            self.net.size.offsetY = bdict["Offset"]["y"]
            self.net.size.sizeY = bdict["Size"]["y"]
        if self.net.size.dimension > 2:
            self.net.size.offsetZ = bdict["Offset"]["z"]
            self.net.size.sizeZ = bdict["Size"]["z"]
        
        self.net.defaultEquation = bdict["DefaultEquation"]
        try:
            self.net.defaultBound = bdict["DefaultBound"]
        except:
            print("DefaultBound not set")
        self.net.defaultInitial = bdict["DefaultInitial"]
        
        for side_num in self.net.boundRegions:
            self.net.boundRegions[side_num].clear()

        dim = self.net.size.dimension
        for boundDict in bdict["BoundRegions"]:
            boundDict.update({'dim': dim})
            # side_num = boundDict['Side']
            self.net.editor.add_bound_region(BoundRegion(**boundDict))
            # self.net.boundRegions.append(BoundRegion(**boundDict))
        for initDict in bdict["InitialRegions"]:
            initDict.update({'dim': dim})
            self.net.initialRegions.append(InitialRegion(**initDict))
        for equatDict in bdict["EquationRegions"]:
            equatDict.update({'dim': dim})
            self.net.editor.add_eq_region(EquationRegion(**equatDict))
            # self.net.equationRegions.append(EquationRegion(**equatDict))

        # depricated
        # self.net.editor.set_sides_default()
        # for side in self.net.sides:
        #    self.net.editor.sinch_side_regions(side)
        #    # side.split_side(rewrite=True)

    def getPropertiesDict(self):
        offsetDict = OrderedDict([("x", self.net.size.offsetX)])
        sizeDict = OrderedDict([("x", self.net.size.sizeX)])
        dim = self.net.size.dimension

        if dim > 1:
            offsetDict.update({"y": self.net.size.offsetY})
            sizeDict.update({"y": self.net.size.sizeY})
        if dim > 2:
            offsetDict.update({"z": self.net.size.offsetZ})
            sizeDict.update({"z": self.net.size.sizeZ})
        propDict = OrderedDict([
            ("Name", self.net.base.name),
            # ("Dimension", self.net.size.dimension),
            ("Offset", offsetDict),
            ("Size", sizeDict),
            ("DefaultEquation", self.net.defaultEquation),
            ("DefaultInitial", self.net.defaultInitial),
            ("DefaultBound", self.net.defaultBound),
            ("BoundRegions", [bdict.getPropertiesDict(dim)
                              for k in self.net.boundRegions.keys()
                              for bdict in self.net.boundRegions[k]]),
            ("InitialRegions", [idict.getPropertiesDict(dim)
                                for idict in self.net.initialRegions]),
            ("EquationRegions", [edict.getPropertiesDict(dim)
                                 for edict in self.net.equationRegions])])
        return propDict
