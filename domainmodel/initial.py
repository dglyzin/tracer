# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict

class Initial(object):
    def __init__(self, name):
        self.name = name
        self.values = ["0"]

    def fillProperties(self, dict):
        self.name = dict["Name"]
        self.values = dict["Values"]        

    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),            
            ("Values", self.values)            
        ])   
        return propDict  

