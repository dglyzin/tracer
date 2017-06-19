from domainmodel.block import Block
from domainmodel.equation import Equation
from domainmodel.model import Model
from domainmodel.funcGenerator import FuncGenerator
from domainmodel.generator2D import Generator2D
from domainmodel.abstractGenerator import AbstractGenerator
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap
import os

def test_binarymodel():
    model = Model()
    inputFile = os.path.join(os.getcwd(),
                             'tests',
                             'short_restest_delay.json')

    model.loadFromFile(inputFile)
    
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    delays = bm.saveFuncs(os.path.join(os.getcwd(),
                                       'tests',
                                       'introduction',
                                       'src',
                                       "outFunctFile.cpp"),
                          "")
    bm.saveDomain(os.path.join(os.getcwd(),
                               'tests',
                               'introduction',
                               'src',
                               "outDataFile.dom"),
                  delays)
    # bm.compileFuncs(OutputFuncFile)
    
