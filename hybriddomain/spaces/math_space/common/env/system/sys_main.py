# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''

# import sys

# python 2 or 3
# if sys.version_info[0] > 2:
#    from objectsTemplate import Object

import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
# print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from env.equation_net.equation import Equation
from env.system.sys_base import sysBase
from env.system.sys_io import sysIO
from env.system.sys_cpp import sysCpp
from env.system.sys_postproc import sysPostProc
from env.system.sys_plot import sysPlotter


class sysNet():

    '''Represent system of equations.
    system can be either strings or Equation objects
    or both.

    TODO:
    Equation as parameter for work with equation_net.

    Examples:
    >>> eq_0 = Equation("U'=D[U, {x, 1}]")
    >>> eq_1 = "V' = D[V, {y, 1}] + U"
    >>> system = System(system=[eq_0, eq_1])

    '''

    def __init__(self, name=None, system=[], vars="x",
                 cpp=False, EqBilder=Equation, lex_terms_db=None):
        self.base = sysBase(self, name, vars, cpp)
        self.io = sysIO(self)
        self.cpp = sysCpp(self)
        self.postproc = sysPostProc(self)
        self.plotter = sysPlotter(self)
        self.EqBilder = EqBilder

        if lex_terms_db is None:
            self.eqs = [EqBilder(sent) if type(sent) == str else sent
                        for sent in system]
        else:
            self.eqs = [EqBilder(sent, db=lex_terms_db)
                        if type(sent) == str else sent
                        for sent in system]

        for i, eq in enumerate(self.eqs):
            try:
                self.eqs[i].parser.parse()
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

    def copy(self):
        copied = sysNet(name=self.base.name,
                        system=[eq.sent for eq in self.eqs],
                        vars=self.base.vars, cpp=self.base.cpp)
        copied.copy_params(self)
        return(copied)

    def copy_params(self, from_system):
        
        '''Copy ``system`` cpp params to self'''

        if len(self.eqs) != len(from_system.eqs):
            raise(BaseException("\nCount of equations in copied"
                                + " systems must be same"))
        for i, eq in enumerate(self.eqs):

            gens_to = eq.replacer.cpp.gen.terms_gens
            gens_from = from_system.eqs[i].replacer.cpp.gen.terms_gens

            for term_name in gens_from:
                params_to = gens_to[term_name].params
                params_from = gens_from[term_name].params
                for param_name in params_from:
                    params_to[param_name] = params_from[param_name]
                 
    def __repr__(self):
        
        return(str([eq.__repr__() for eq in self.eqs]))
            
