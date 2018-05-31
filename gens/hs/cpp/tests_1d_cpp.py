'''
Generated files will be in:
   tests/src/generated/file_name/file_name.cpp

Tests:
>>> import gens.hs.cpp.tests_1d_cpp as ts
>>> out = ts.test_templates_1d('tests/test1d_two_blocks0.json')
>>> err = ts.test_cpp('test1d_two_blocks0.cpp', 1)
>>> err
True
'''
from gens.hs.cpp.common.definitions import Gen as GenDef
from gens.hs.cpp.common.initials import Gen as GenInit
from gens.hs.cpp.common.params import Gen as GenParams
from gens.hs.cpp.common.centrals import Gen as GenCent
from gens.hs.cpp.d1.bounds import Gen as GenBounds
from gens.hs.cpp.d1.interconnects import Gen as GenIcs
from gens.hs.cpp.common.array import Gen as GenArr

from envs.hs.model.model_main import ModelNet as Model

import os
import subprocess
import shutil

import logging

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tests.py')
logger.setLevel(level=log_level)


def test_templates_1d(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for 1d.

    out will be in:
       'tests/src/from_test_template_1d.cpp'

    '''

    out = test_template_definitions(modelFile)
    out += test_template_initials(modelFile)
    out += test_template_params(modelFile)

    funcNameStack = []

    outl, funcNameStackl = test_template_centrals(modelFile)
    funcNameStack.extend(funcNameStackl)
    # remove duplicates:
    funcNameStack = list(set(funcNameStack))
    out += outl

    outl, funcNameStackl = test_template_interconnects(modelFile)
    funcNameStack.extend(funcNameStackl)
    # remove duplicates:
    funcNameStack = list(set(funcNameStack))
    out += outl

    outl, params = test_template_bounds(modelFile)
    funcNameStack.extend(funcNameStackl)
    # remove duplicates:
    funcNameStack = list(set(funcNameStack))
    out += outl

    out += test_template_array(funcNameStack)

    # print(out)
    
    # out = params.postprocessing(out)

    name = os.path.basename(modelFile)
    to_file(out, name)
    return(out)


def test_template_array(funcNamesStack):
    '''
    DESCRIPTION:
    Generate cpp for centrals from
    template.

    
    funcNamesStack contained in each generator
    after call:
     gen_cent.set_params_for_centrals
     gen_inc.set_params_for_interconnects
     gen_bounds.set_params_for_bounds
    for them.

    template in :
       'templates/array.template'

    out will be in:
       'tests/introduction/src/from_test_template_array.cpp'

    INPUT:
    params from central, interconnect, bounds
    '''
    gen = GenArr()

    gen.set_params_for_array(funcNamesStack)
    out = gen.get_out_for_array()

    # to_file(out, 'from_test_template_array.cpp')

    return(out)


def test_template_interconnects(modelFile="tests/test1d_two_blocks0.json", params=None):
    '''
    DESCRIPTION:
    Generate cpp for interconnects from
    template.

    template in :
       'templates/interconnects.template'

    out will be in:
       'tests/introduction/src/from_test_template_interconnects.cpp'

    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile
    '''
    if params is None:
        params = Params()
    else:
        # for delays from other templates
        try:
            dataTermVarsForDelay = params.dataTermVarsForDelay
        except:
            dataTermVarsForDelay = None
    '''
    gen = GenIcs()

    # parameters for interconnect
    gen.set_params_for_interconnects(model)

    out = gen.get_out_for_interconnects()
    
    # to_file(out, 'from_test_template_interconnects.cpp')

    # for delays
    # params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

    return((out, gen.funcNamesStack))


def test_template_bounds(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for bounds from
    template.

    It always placed after test_template_interconnects
    because if interconnect exist for some side then
    ignore it bound.

    template in :
       'templates/bound_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_bounds.cpp'

    INPUT:
    param from test_template_interconnects
    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    '''
    if params is None:
        params = Params()
    else:
        # for delays from other templates
        try:
            dataTermVarsForDelay = params.dataTermVarsForDelay
        except:
            dataTermVarsForDelay = None
    '''
    gen = GenBounds()
    '''
    # for delays
    if dataTermVarsForDelay is not None:
        parser.cppOut.dataTermVarsForDelay = dataTermVarsForDelay
    '''
    # parameters for bound
    gen.set_params_for_bounds(model)
    '''
    for bound in gen.bounds:
        if bound.btype == 0:
            # Dirichlet
            bound.parsedValues = bound.values
        else:
            # Neuman
    '''
    out = gen.get_out_for_bounds()
    
    # to_file(out, 'from_test_template_bounds.cpp')
    '''
    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay
    '''
    return((out, gen.funcNamesStack))


def test_template_centrals(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for centrals from
    template.

    template in :
       'templates/central_functions.template'

    out will be in:
       'tests/introduction/src/from_test_template_centrals.cpp'

    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    # model = get_model_for_tests(modelFile)
    gen = GenCent()
    
    # parameters for central
    gen.set_params_for_centrals(model)
    out = gen.get_out_for_centrals()
    
    # to_file(out, 'from_test_template_centrals.cpp')

    # for delays
    # params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

    return((out, gen.funcNamesStack))


def test_template_params(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for params from
    template.

    template in :
       'templates/params.template'

    out will be in:
       'tests/introduction/src/from_test_template_params.cpp'
    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    gen = GenParams()

    # model = get_model_for_tests(modelFile)
    gen.set_params_for_parameters(model)
    out = gen.get_out_for_parameters()
    # to_file(out, 'from_test_template_params.cpp')

    return(out)


def test_template_initials(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for initial and Dirichlet from
    template example.

    template in :
       'templates/initial_conditions.template'

    out will be in:
       'tests/introduction/src/from_test_template_initial.cpp'
    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    gen = GenInit()

    # model = get_model_for_tests(modelFile)
    gen.set_params_for_initials(model)
    
    # params.dim = dim
    out = gen.get_out_for_initials()
    # to_file(out, 'from_test_template_initials.cpp')

    return(out)


def test_template_definitions(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    Generate cpp for definitions from
    template.

    template in :
       'templates/definitions.template'

    out will be in:
       'tests/introduction/src/from_test_template_definitions.cpp'

    '''
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    gen = GenDef()

    # parameters for definitions
    gen.set_params_for_definitions(model)
    
    out = gen.get_out_for_definitions()

    # to_file(out, 'from_test_template_definitions.cpp')

    return(out)


def get_model_for_tests(modelFile="tests/test1d_two_blocks0.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.io.loadFromFile(modelFile)
    return(model)


def to_file(out, fileName):

    '''fileName Used to create folder in
    tests/src folder and put output here
    (ex: out.cpp)'''
    
    folderName = fileName.split('.')[0]
    fileName = folderName + '.cpp'
    folder = os.path.join('tests', 'src',
                          'generated', folderName)
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        shutil.rmtree(folder)
        os.makedirs(folder)
    
    path = os.path.join(folder, fileName)
    logger.debug("path =")
    logger.debug(path)
    
    f = open(path, 'w')
    f.write(out)
    f.close()

    pathFrom = os.path.join('tests', 'src', 'libs', 'libuserfuncs.so')
    shutil.copy2(pathFrom, folder)

    pathFrom = os.path.join('tests', 'src', 'libs', 'userfuncs.h')
    shutil.copy2(pathFrom, folder)


def test_cpp(fileName, _stderr=None):
    '''
    DESCRIPTION:
    Test generated file by gcc.
    File should be in "/hybriddomain/tests/src"
    folder and libuserfuncs.so, userfuncs.h also
    '''
    logger.debug("FROM test_cpp")
    curDir = os.getcwd()

    # assuming that this file launched from hybriddomain
    folderName = fileName.split('.')[0]
    path = os.path.join(curDir, 'tests', 'src',
                        'generated', folderName)
    cpp = os.path.join(path, fileName)
    lib = os.path.join(path, 'libuserfuncs.so')

    # change bad path
    '''
    f = open(cpp)
    data = f.read()
    f.close()
    data = data.replace("prepr_folder_path/doc/userfuncs.h", "userfuncs.h")
    f = open(cpp, 'w')
    f.write(data)
    f.close()
    '''

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

    # byte to str:
    out = out.decode("utf-8")
    err = err.decode("utf-8")

    if (err is not None and len(err) > 0):
        if _stderr is None:
            raise(GccException(err))
        else:
            return(err)
    
    if _stderr is not None:
        logger.info("out")
        logger.info(out)
        logger.info("err")
        logger.info(err)
    if err is None or len(err) == 0:
        return(True)


class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err
        logger.error(self.err)
