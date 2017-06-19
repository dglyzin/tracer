# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

from collections import OrderedDict

'''
Description of hardware resources available for core launch.
Memory is in Gigabytes
'''
class Compnode(object):
    def __init__(self):
        self.name = "cnode1"
        self.cpuCount = 1
        self.cpuMemory = [1]
        self.gpuCount = 0
        self.cpuMemory = []
        
    def fillProperties(self,ndict):
        self.name = ndict["Name"]
        self.cpuCount = ndict["CpuCount"]
        try:
            self.cpuMemory = ndict["CpuMemory"]
        except:
            pass
        self.gpuCount = ndict["GpuCount"]
        try:
            self.gpuMemory = ndict["GpuMemory"]
        except:
            pass
        
    def getPropertiesDict(self):          
        return OrderedDict([
                            ("Name", self.name),
                            ("CpuCount", self.cpuCount),
                            ("CpuMemory", self.cpuMemory),
                            ("GpuCount", self.gpuCount) 
                            ("GpuMemory", self.gpuMemory),                 
                            ])