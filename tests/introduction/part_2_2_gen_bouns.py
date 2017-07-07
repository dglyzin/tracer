'''
DESCRIPTION:

Example of blocks configuration:

"Blocks": [
        {
            "Name": "MainBlock", 
            "Offset": {
                "x": 0.0
            }, 
            "Size": {
                "x": 1.0
            }, 
            "DefaultEquation": 0, 
            "DefaultInitial": 0, 
            "BoundRegions": [
                {
                    "BoundNumber": 0,  # number of bound in "Bounds" list  
                    "Side": 2, 
                    "xfrom": 0.25, 
                    "xto": 0.75, 
                    "yfrom": 0.0, 
                    "yto": 0.0
                }
            ], 
            "InitialRegions": [
                {
                    "InitialNumber": 1,  # number of initial in "Initials" list
                    "xfrom": 0.0, 
                    "xto": 0.1
                }
            ], 
            "EquationRegions": [
                {
                    "EquationNumber": 1,  # number of equation in "Equations" list
                    "xfrom": 0.4, 
                    "xto": 0.6, 
                    "yfrom": 0.4, 
                    "yto": 0.6
                }
            ]
        }
    ], 
    "Interconnects": [
        {
            "Name": "connection 1", 
            "Block1": 0,  # number of block in "Blocks" list
            "Block2": 0, 
            "Block1Side": 1, 
            "Block2Side": 0
        }
    ], 
    "Equations": [
        {
            "Name": "1D heat 1", 
            "Vars": [
                "x"
            ], 
            "System": [
                "U'= D[U,{x,2}]"
            ]
        },
        {
            "Name": "Flat Brusselator", 
            "Vars": [
                "x", 
                "y"
            ], 
            "System": [
                "U'=2.0 - V", 
                "V'=-2.0", 
                "M'=a + (M^2) * N - (b+1) * M + c * (D[M,{x,2}] + D[M,{y,2}])", 
                "N'=b * M - (M^2) * N + c * (D[N,{x,2}] + D[N,{y,2}])"
            ]
        }
    ], 
    "EquationParams": {
        "Params": [
            "a", 
            "c", 
            "f"
        ], 
        "ParamValues": [
            {
                "a": 1.0, 
                "c": 0.1, 
                "f": 1.0
            }
        ], 
        "DefaultParamsIndex": 0
    }, 
     "Bounds": [
        {
            "Name": "N 1", 
            "Type": 1, 
            "Values": [ # for each (U, V, M, N)
                "50.0",
                "50.0",
                "50.0",
                "50.0"
            ]
        }
    ],
    "Initials": [
        {
            "Name": "Initial values 0", 
            "Values": [
                "0.0"
            ]
        }, 
        {
            "Name": "Initial values 1", 
            "Values": [
                "100.0"
            ]
        }
    ], 
'''
from part_2_generators import Equation, get_gen_for_test
from part_2_generators import AbstractGenerator, Generator2D
import os
from domainmodel.objectsTemplate import Object


class BlockInfo(Object):
    def __init__(self, block):
        self.block = block

        self.systemsForCentralFuncs = None
        self.numsForSystems = None
        self.totalBCondLst = None
        self.totalInterconnectLst = None
        self.blockFuncMap = None
    
    def getBlockInfo(self, gen, blockNumber):
        data = gen.getBlockInfo(self.block, blockNumber)

        self.systemsForCentralFuncs = data[0]
        self.numsForSystems = data[1]
        self.totalBCondLst = data[2]
        self.totalInterconnectLst = data[3]
        self.blockFuncMap = data[4]

    def getPropertiesDict(self):
        return(self.__dict__)


def test_getBlockInfo(modelFile="tests/short_restest_full.json"):
    gen = get_gen_for_test(modelFile).generator

    gen.generateAllDefinitions()
    
    totalArrWithFunctionNames = list()
    functionMaps = []

    blockInfo = BlockInfo(gen.blocks[0])
    blockInfo.getBlockInfo(gen, 0)
    return(blockInfo)


def test_bound(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What bounds is.

    EXAMPLE:
    1d:
    "tests/brusselator1d_bound_U.json"
    '''
    gen = get_gen_for_test(modelFile).generator

    gen.generateAllDefinitions()
    
    blockInfo = BlockInfo(gen.blocks[0])
    blockInfo.getBlockInfo(gen, 0)

    cf, arrWithFunctionNames = gen.generateCentralFunctionCode(gen.blocks[0], 0,
                                                               blockInfo.systemsForCentralFuncs,
                                                               blockInfo.numsForSystems)

    # prabobly main for bounds
    bf = gen.generateBoundsAndIcs(gen.blocks[0], 0,
                                  arrWithFunctionNames,
                                  blockInfo.blockFuncMap,
                                  blockInfo.totalBCondLst,
                                  blockInfo.totalInterconnectLst)
    # write to file
    to_file(bf)
    # return(totalBCondLst)


def to_file(out):

    f = open(os.path.join(os.getcwd(), 'tests',
                          'introduction',
                          'src', 'some_functions.cpp'),
             'w')
    f.write(out)
    f.close()
