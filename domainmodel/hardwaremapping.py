# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from collections import OrderedDict

'''
Description of hardware resources available for core launch.
'''
class CompNode(object):
    def __init__(self, ndict):
        self.name = ndict["Name"]
        self.cpuCount = ndict["CpuCount"]
        self.gpuCount = ndict["GpuCount"]

class Hardware(object):
    def __init__(self, nodelist):
        self.fillProperties(nodelist)

    def fillProperties(self, nodelist):
        self.nodes = [CompNode(ndict) for ndict in nodelist] 

    def getDeviceCount(self):
        return sum([node.cpuCount+node.gpuCount for node in self.nodes])         
    
    def getPropertiesDict(self):          
        propDict = [ OrderedDict([
                                  ("Name", node.name),
                                  ("CpuCount", node.cpuCount),
                                  ("GpuCount", node.gpuCount)                   
                                  ]
                            for node in self.nodes)
                    ]   
        return propDict  
