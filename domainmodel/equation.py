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