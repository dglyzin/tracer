# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict

class Bound(object):
    def __init__(self, name):
        self.name = name
        self.btype = 0
        self.values = ["0"]

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.btype = dict["Type"]
        self.values = dict["Values"]        
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Type", self.btype),
            ("Values", self.values)            
        ])   
        return propDict  