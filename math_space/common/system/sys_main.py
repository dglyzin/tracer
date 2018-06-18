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
from math_space.common.system.sys_cpp import sysCpp


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
        self.cpp = sysCpp(self)

        self.eqs = [Equation(sent) if type(sent) == str else sent
                    for sent in system]
        for i, eq in enumerate(self.eqs):
            try:
                self.eqs[i].parse()
            except:
                raise(SyntaxError("eq %s not supported" % eq.sent))
    
    def __getitem__(self, k):
        return(self.eqs[k])

    def __setitem__(self, k, v):
        self.eqs[k] = v

    def append(self, v):
        self.eqs.append(v)

    def __len__(self):
        return(len(self.eqs))
