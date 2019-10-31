# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict
import sys

from hybriddomain.spaces.math_space.common.env.system.sys_main import sysNet as System

# python 2 or 3
# if sys.version_info[0] > 2:
#    from objectsTemplate import Object

bdict = {"dirichlet": 0, "neumann": 1}


class Bound():
    def __init__(self, name=None, eq=None, btype=0):
        self.name = name
        self.btype = 0
        self.equation = eq
        self.values = System(system=["0"])
        self.derivative = ["0"]

    def __eq__(self, o):

        '''Equality is difined with all attributs, except boundNumber,
        because it depends only of order in model.bounds list'''

        cond = (self.name == o.name and self.btype == o.btype
                and self.equation == o.equation
                and self.values == o.values
                and self.derivative == o.derivative)
        return(cond)

    def fillProperties(self, bdict):
        self.name = bdict["Name"]
        self.btype = bdict["Type"]
        self.values = bdict["Values"]
        self.system = System(system=bdict["Values"])
        if self.btype == 0:
            self.derivative = bdict["Derivative"]
    
    def getPropertiesDict(self):
        propDict = OrderedDict([
            ("Name", self.name),
            ("Type", self.btype),
            ("Values", self.values),
            ("Equation", self.equation)])
        if self.btype == 0:
            propDict.setdefault("Derivative", self.derivative)
        return(propDict)
