# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from collections import OrderedDict
      
class Equation(object):
    def __init__(self, name):
        self.name = name
        self.vars = "x"
        self.system = ["U'=1"]

    def fillProperties(self, edict):
        self.name = edict["Name"]
        self.vars = edict["Vars"]
        self.system = edict["System"]
        self.params = edict["Params"]
        self.paramValues = edict["ParamValues"]
   
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Vars", self.vars),
            ("System", self.system),
            ("Params", self.params),
            ("ParamValues", self.paramValues)
        ])   
        return propDict  