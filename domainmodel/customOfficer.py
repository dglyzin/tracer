# -*- coding: utf-8 -*-
'''
Created on 02 июля 2015 г.

@author: golubenets
'''
class Reviewer:
    def __init__(self, equations, blocks, initials, bounds, gridStep, params, paramValues, defaultParamsIndex):
        self.equations = equations
        self.blocks = blocks
        self.initials = initials
        self.bounds = bounds
        self.gridStep = gridStep
        self.params = params
        self.paramValues = paramValues
        self.defaultParamsIndex = defaultParamsIndex
    
    def ReviewInput(self):
        self.ReviewParameters()
        
    def ReviewParameters(self):
        paramsCount = len(self.params)
        nonrequrringParamsCnt = len(set(self.params))
        if paramsCount != nonrequrringParamsCnt:
            raise AttributeError("Some parameter occurs more than once in list of parameters!")
        for idx, value in enumerate(self.paramValues):
            if len(value) != paramsCount:
                raise AttributeError("Count of parameter values in dictionary with index "+str(idx)+" doesn't correspond to count of parameters!")
            for parameter in value:
                if parameter not in self.params:
                    raise AttributeError("Parameter '"+parameter+"' is absent in list of parameters, but it is in dictionary with index "+str(idx)+" in list of parameter values!")
                