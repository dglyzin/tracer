from collections import OrderedDict
from math_space.common.equation.equation import Equation


class sysIO():
    def __init__(self, net):
        self.net = net

    def fillProperties(self, edict):
        self.net.base.name = edict["Name"]
        self.net.base.vars = edict["Vars"]
        self.net.eqs = [Equation(sent) for sent in edict["System"]]

    def getPropertiesDict(self):
        propDict = OrderedDict([
            ("Name", self.net.base.name),
            ("Vars", self.net.base.vars),
            ("System", [eq.sent for eq in self.net.eqs])
        ])
        return(propDict)
