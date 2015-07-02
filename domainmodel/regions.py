# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict

class BoundRegion(object):
    def __init__(self, bdict, dimension):
        self.boundNumber = bdict["BoundNumber"]
        self.side = bdict["Side"]
        if dimension>1:
            self.xfrom = bdict["xfrom"]
            self.xto = bdict["xto"]
            self.yfrom = bdict["yfrom"]
            self.yto = bdict["yto"]
        if dimension>2:
            self.zfrom = bdict["zfrom"]
            self.zto = bdict["zto"]
    
       
    def getPropertiesDict(self, dimension):
        propDict = OrderedDict([            
            ("BoundNumber", self.boundNumber),
            ("Side", self.side)
        ])   
        if dimension>1:
            propDict.update({"xfrom":self.xfrom})
            propDict.update({"xto":self.xto})
            propDict.update({"yfrom":self.yfrom})
            propDict.update({"yto":self.yto})
        if dimension>2:
            propDict.update({"zfrom":self.zfrom})
            propDict.update({"zto":self.zto})
        return propDict  


class InitialRegion(object):
    def __init__(self, bdict, dimension):
        self.initialNumber = bdict["InitialNumber"]        
        self.xfrom = bdict["xfrom"]
        self.xto = bdict["xto"]
        if dimension>1:            
            self.yfrom = bdict["yfrom"]
            self.yto = bdict["yto"]
        if dimension>2:
            self.zfrom = bdict["zfrom"]
            self.zto = bdict["zto"]
        
     
    
    def getPropertiesDict(self, dimension):
        propDict = OrderedDict([            
            ("InitialNumber", self.initialNumber),
            ("xfrom", self.xfrom),
            ("xto", self.xto)
        ])   
        if dimension>1:            
            propDict.update({"yfrom":self.yfrom})
            propDict.update({"yto":self.yto})
        if dimension>2:
            propDict.update({"zfrom":self.zfrom})
            propDict.update({"zto":self.zto})
        return propDict  

class EquationRegion(object):
    def __init__(self, bdict, dimension):
        self.equationNumber = bdict["EquationNumber"]        
        self.xfrom = bdict["xfrom"]
        self.xto = bdict["xto"]
        if dimension>1:            
            self.yfrom = bdict["yfrom"]
            self.yto = bdict["yto"]
        if dimension>2:
            self.zfrom = bdict["zfrom"]
            self.zto = bdict["zto"]
        
      
    def getPropertiesDict(self, dimension):
        propDict = OrderedDict([            
            ("EquationNumber", self.equationNumber),
            ("xfrom", self.xfrom),
            ("xto", self.xto)
        ])   
        if dimension>1:            
            propDict.update({"yfrom":self.yfrom})
            propDict.update({"yto":self.yto})
        if dimension>2:
            propDict.update({"zfrom":self.zfrom})
            propDict.update({"zto":self.zto})
        return propDict