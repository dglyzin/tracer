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
from hybriddomain.gens.hs.gen_env.cpp.env.definitions.def_main import Gen as GenDef
from hybriddomain.gens.hs.gen_env.cpp.env.initials.initials_main import Gen as GenInit
from hybriddomain.gens.hs.gen_env.cpp.env.params.params_main import Gen as GenParams
from hybriddomain.gens.hs.gen_env.cpp.env.centrals.cent_main import Gen as GenCent
from hybriddomain.gens.hs.gen_env.cpp.env.bounds.bounds_main import GenD1 as GenBounds
from hybriddomain.gens.hs.gen_env.cpp.env.ics.ics_main import GenD1 as GenIcs
from hybriddomain.gens.hs.gen_env.cpp.env.array.array_main import Gen as GenArr

from hybriddomain.tests.tests_common import to_file, get_model_for_tests

import os

import logging

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tests_1d_cpp.py')
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

    funcNamesStack = []

    outl, funcNamesStackl = test_template_centrals(modelFile)
    funcNamesStack.extend(funcNamesStackl)
    # remove duplicates:
    funcNamesStack = list(set(funcNamesStack))
    out += outl

    outl, funcNamesStackl = test_template_interconnects(modelFile)
    funcNamesStack.extend(funcNamesStackl)
    # remove duplicates:
    funcNamesStack = list(set(funcNamesStack))
    out += outl

    outl, params = test_template_bounds(modelFile)
    funcNamesStack.extend(funcNamesStackl)
    # remove duplicates:
    funcNamesStack = list(set(funcNamesStack))
    out += outl

    out += test_template_array(funcNamesStack)

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

    gen.common.set_params_for_array(funcNamesStack)
    out = gen.cpp_render.get_out_for_array()

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
    funcNamesStack = []
    gen.common.set_params_for_interconnects(model, funcNamesStack)

    out = gen.cpp_render.get_out_for_interconnects()
    
    # to_file(out, 'from_test_template_interconnects.cpp')

    # for delays
    # params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

    return((out, gen.params.funcNamesStack))


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
    funcNamesStack = []
    gen.common.set_params_for_bounds(model, funcNamesStack)
    '''
    for bound in gen.bounds:
        if bound.btype == 0:
            # Dirichlet
            bound.parsedValues = bound.values
        else:
            # Neuman
    '''
    out = gen.cpp_render.get_out_for_bounds()
    
    # to_file(out, 'from_test_template_bounds.cpp')
    '''
    # for delays
    params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay
    '''
    return((out, gen.params.funcNamesStack))


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
    funcNamesStack = []
    gen.common.set_params_for_centrals(model, funcNamesStack)
    out = gen.cpp_render.get_out_for_centrals()
    
    # to_file(out, 'from_test_template_centrals.cpp')

    # for delays
    # params.dataTermVarsForDelay = parser.cppOut.dataTermVarsForDelay

    return((out, gen.params.funcNamesStack))


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
    gen.cpp.set_params_for_parameters(model)
    out = gen.cpp_render.get_out_for_parameters()
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
    gen.cpp.set_params_for_initials(model)
    
    # params.dim = dim
    out = gen.cpp_render.get_out_for_initials()
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
    gen.common.set_params_for_definitions(model)
    
    out = gen.cpp_render.get_out_for_definitions()

    # to_file(out, 'from_test_template_definitions.cpp')

    return(out)


