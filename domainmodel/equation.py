# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from collections import OrderedDict
import sys

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.objectsTemplate import Object
else:
    from objectsTemplate import Object


class Equation(Object):
    def __init__(self, name):
        self.name = name
        self.vars = "x"
        self.system = ["U'=1"]
        self.cpp = False

    def fillProperties(self, edict):
        self.name = edict["Name"]
        self.vars = edict["Vars"]
        self.system = edict["System"]
   
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Vars", self.vars),
            ("System", self.system)
        ])
        return propDict  
