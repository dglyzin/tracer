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
		if len(edict["Params"]) != 0 and len(edict["ParamValues"]) == 0:
		    raise AttributeError("The system has some parameters, but their values was not specified!")
		if len(edict["Params"]) == 0 and len(edict["ParamValues"]) != 0:
		    raise AttributeError("The system hasn't any parameters, but the field ParamValues is not empty!")
		self.params = edict["Params"]
        self.paramValues = edict["ParamValues"]
		if len(self.paramValues) > 1:
			self.defaultParamsIndex = edict["DefaulParamsIndex"]
   
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Vars", self.vars),
            ("System", self.system),
            ("Params", self.params),
            ("ParamValues", self.paramValues)
        ])   
        return propDict  