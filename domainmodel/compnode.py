# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from collections import OrderedDict

'''
Description of hardware resources available for core launch.
'''
class Compnode(object):
    def __init__(self):
        self.name = "cnode1"
        self.cpuCount = 1
        self.gpuCount = 0
        
    def fillProperties(self,ndict):
        self.name = ndict["Name"]
        self.cpuCount = ndict["CpuCount"]
        self.gpuCount = ndict["GpuCount"]
        
    def getPropertiesDict(self):          
        return OrderedDict([
                            ("Name", self.name),
                            ("CpuCount", self.cpuCount),
                            ("GpuCount", self.gpuCount)                   
                            ])