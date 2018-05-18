# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

# import sys

# python 2 or 3
# if sys.version_info[0] > 2:
#    from objectsTemplate import Object

from math_space.common.equation.equation import Equation
from math_space.common.system.sys_base import sysBase
from math_space.common.system.sys_io import sysIO


class sysNet():

    '''Represent system of equations.
    system can be either strings or Equation objects
    or both.
    
    Examples:
    >>> eq_0 = Equation("U'=D[U, {x, 1}]")
    >>> eq_1 = "V' = D[V, {y, 1}] + U"
    >>> system = System(system=[eq_0, eq_1])

    '''

    def __init__(self, name=None, system=[], vars="x", cpp=False):
        self.base = sysBase(self, name, vars, cpp)
        self.io = sysIO(self)
        
        self.eqs = [Equation(sent) if type(sent) == str else sent
                    for sent in system]

    
