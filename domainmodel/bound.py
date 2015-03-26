# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
bdict = {"dirichlet":0, "neumann":1}

from collections import OrderedDict

class Bound(object):
    def __init__(self, name):
        self.name = name
        self.btype = 0
        self.values = ["0"]

    def fillProperties(self, bdict):
        self.name = bdict["Name"]
        self.btype = bdict["Type"]
        self.values = bdict["Values"]
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Type", self.btype),
            ("Values", self.values)
        ])
        return propDict  