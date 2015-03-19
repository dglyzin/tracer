# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin

'''
from collections import OrderedDict


class Interconnect(object):
    def __init__(self, name):
        self.name = name
        self.block1 = 0
        self.block2 = 0
        self.block1Side = 0
        self.block2Side = 1

    def fillProperties(self, idict):
        self.name = idict["Name"]
        self.block1 = idict["Block1"]
        self.block2 = idict["Block2"]
        self.block1Side = idict["Block1Side"]
        self.block2Side = idict["Block2Side"]
    
    def getPropertiesDict(self):          
        propDict = OrderedDict([            
            ("Name", self.name),
            ("Block1", self.block1),
            ("Block2", self.block2),
            ("Block1Side", self.block1Side),
            ("Block2Side", self.block2Side)       
        ])   
        return propDict  