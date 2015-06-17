# -*- coding: utf-8 -*-
#from funcGenerator import FunctionCodeGenerator
from model import Model

mod = Model()
mod.loadFromFile("../tests/test3_heat_wbounds0.json")
mod.createCPP("FunctionsNew.cpp")
print "Done! See FunctionsNew.cpp"