# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin

'''

from envs.hs.interconnect.ic_base import icBase
from envs.hs.interconnect.ic_io import icIO
from envs.hs.interconnect.ic_plot import icPlotter
from envs.hs.interconnect.ic_dom import icDom


class icMain():
    def __init__(self, name, model=None,
                 blockNumber1=0, blockNumber2=1,
                 block1Side=0, block2Side=1):
        
        self.base = icBase(self, name,
                           blockNumber1, blockNumber2,
                           block1Side, block2Side)
        self.io = icIO(self)
        self.plotter = icPlotter(self)
        self.dom = icDom(self)

        self.set_model(model)

    def set_model(self, model):

        self.model = model
        if model is not None:
            if self not in self.model.interconnects:
                self.model.interconnects.append(self)

    def __eq__(self, o):
        cond = (self.block1 == o.block1
                and self.block2 == o.block2
                and self.block1Side == o.block1Side
                and self.block2Side == o.block2Side)
        return(cond)

    def __repr__(self):
        out = "\nic: %s\n" % (str(self.base.name))
        out += "blockNumber1: %s\n" % (str(self.block1))
        out += "blockNumber2: %s\n" % (str(self.block2))
        out += "block1Side1: %s\n" % (str(self.block1Side))
        out += "block1Side2: %s\n" % (str(self.block2Side))

        return(out)
