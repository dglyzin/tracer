'''
DESCRIPTION:
Some functions for understanding how
generators of .cpp code work.

For generate and test cpp:
import tests.introduction.part_2_generators as p2
p2.test_model_create_cpp(testFile)
p2.test_cpp()

From most general to particlular.

SHEME OF ABSTRACTIONs:
model.createCPPandGetFunctionMaps
uses
   FuncGenerator.generateAllFunctions
        from funcGenerator.py
   uses
      AbstractGenerator.generateCentralFunctionCode
         from abstractGenerator.py
      uses
         MathExpressionParser.parseMathExpression
          from equationParser.py
         and
         RHSCodeGenerator.generateRightHandSideCode{..Delay}
          from rhsCodeGenerator.py
'''
from domainmodel.model import Model
from domainmodel.funcGenerator import FuncGenerator

import os
import logging
import subprocess

# create logger that child of tests.tester loger
logger = logging.getLogger('tests.tester.part_2_generators')


def test_logger():
    '''
    DESCRIPTION:
    For demonstration. See tests/tester.py
    Call from tester.py  will use
    it as parent. (because of name in getLogger)
    See:
    https://docs.python.org/2.7/howto/logging-cookbook.html#using-logging-in-multiple-modules
    '''
    logger.info("logger info")
    logger.debug("logger debug")
    logger.error("logger error")


def get_gen_for_test(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What is generator.
    Create generator for all tests.

    EXAMPLE:
    "tests/brusselator1d_bound_U.json"
    '''
    # load model
    model = get_model_for_tests(modelFile)

    gridStep = [model.gridStepX, model.gridStepY, model.gridStepZ]
    haloSize = model.getHaloSize()
    mDO = model.getMaxDerivOrder()
    delay_lst = model.determineDelay()

    print("delay_lst = ")
    print(delay_lst)
    
    gen = FuncGenerator(delay_lst, mDO, haloSize, model.equations,
                        model.blocks, model.initials, model.bounds,
                        model.interconnects, gridStep, model.params,
                        model.paramValues, model.defaultParamsIndex,
                        preprocessorFolder="some_folder")
    return(gen)


def get_model_for_tests(modelFile="tests/short_restest_full.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def test_model_create_cpp(modelFile="tests/brusselator1d_bound_U.json"):
    '''
    DESCRIPTION:
    How .json become .cpp.
    .json = "hybriddomain/tests/short_restest_delay.json"
    .cpp =  "hybriddomain/tests/introduction/src/
                short_restest_delay.cpp"
    '''
    logger.debug("FROM test_model_create_cpp")

    fileName = os.path.basename(modelFile)
    # removing type
    fileName = fileName.split('.')[0]
    # add new type
    fileName = fileName + '.cpp'
    path = os.path.join("tests/introduction/src", fileName)
    # load model
    model = get_model_for_tests(modelFile)
    forDomain = model.createCPPandGetFunctionMaps(path,
                                                  "prepr_folder_path")
    logger.debug("path = %s" % path)
    logger.debug("modelFile = %s" % modelFile)

    return(forDomain)


def test_cpp(fileName='from_model_createCPP.cpp', _stderr=None):
    '''
    DESCRIPTION:
    Test generated file by gcc.
    File should be in "/hybriddomain/tests/indtroduction/src"
    folder and libuserfuncs.so, userfuncs.h also
    '''
    logger.debug("FROM test_cpp")
    curDir = os.getcwd()

    # assuming that this file launched from domainmodel
    path = os.path.join(curDir,
                        'tests',
                        'introduction',
                        'src')
    cpp = os.path.join(path, fileName)
    lib = os.path.join(path, 'libuserfuncs.so')

    # change bad path
    f = open(cpp)
    data = f.read()
    f.close()
    data = data.replace("prepr_folder_path/doc/userfuncs.h", "userfuncs.h")
    f = open(cpp, 'w')
    f.write(data)
    f.close()

    # call gcc
    cmd = ['gcc', cpp, '-shared', '-O3', '-o',
           lib, '-fPIC']
    logger.debug("cmd = %s" % str(cmd))
    
    '''
    stdout and stderr PIPE means
    that new child stream will be created
    so standart output will be unused.
    See:
    https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
    https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
    '''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if (err is not None and len(err) > 0
        and _stderr is None):
        raise(GccException(err))
    if _stderr is not None:
        print("out")
        print(out)
        print("err")
        print(err)

    return(out)


def test_func_gen():
    '''
    DESCRIPTION:
    What is funcGenerator.
    
    '''

    # load gen
    gen = get_gen_for_test()

    outputStr, functionMaps = gen.generateAllFunctions()

    return(outputStr, functionMaps)


class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err
