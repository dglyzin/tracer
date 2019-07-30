# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict

from spaces.math_space.common.env.system.sys_main import sysNet as System


class Initial(object):
    def __init__(self, name):
        self.name = name
        self.values = System(system=["0"])

    def __eq__(self, o):

        '''Equality is difined with all attributs, except initialNumber,
        because it depends only of order in model.initials list'''

        cond = (self.name == o.name
                and self.values == o.values)
        return(cond)

    def fillProperties(self, bdict):
        self.name = bdict["Name"]
        self.values = bdict["Values"]
        self.system = System(system=bdict["Values"])

    def getPropertiesDict(self):
        propDict = OrderedDict([
            ("Name", self.name),
            ("Values", self.values)])
        return propDict

