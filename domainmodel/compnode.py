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
        self.gpuMemory = []
        
    def fillProperties(self,ndict):
        self.name = ndict["Name"]
        self.cpuCount = ndict["CpuCount"]
        #self.cpuMemory = self.cpuCount * [56]
        self.cpuMemory = ndict["CpuMemory"]
        
        self.gpuCount = ndict["GpuCount"]
        self.gpuMemory = ndict["GpuMemory"]
        #self.gpuMemory = self.gpuCount * [5]
        
    def getPropertiesDict(self):          
        return OrderedDict([
                            ("Name", self.name),
                            ("CpuCount", self.cpuCount),
                            ("CpuMemory", self.cpuMemory),
                            ("GpuCount", self.gpuCount), 
                            ("GpuMemory", self.gpuMemory)                 
                            ])