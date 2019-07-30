from tests.tests_common import to_file, get_model_for_tests
from gens.hs.env.centrals.cent_main import Gen as GenCent
from gens.hs.env.bounds.bounds_main import GenD1 as GenBounds
from gens.hs.env.ics.ics_main import GenD1 as GenIcs
from gens.hs.env.array.array_main import Gen as GenArr

import logging

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tests_1d_dom.py')
logger.setLevel(level=log_level)


def test_domain_1d(modelFile="tests/test1d_two_blocks0.json"):
    
    if type(modelFile) == str:
        model = get_model_for_tests(modelFile)
    else:
        model = modelFile

    gen_cent = GenCent()
    gen_bounds = GenBounds()
    gen_ics = GenIcs()
    gen_array = GenArr()

    # FOR funcNameStack
    funcNamesStack = []

    gen_cent.common.set_params_for_centrals(model, funcNamesStack)
    # funcNamesStack.extend(gen_cent.params.funcNamesStack)

    logger.debug("funcNamesStack after cent:")
    logger.debug(funcNamesStack)

    gen_ics.common.set_params_for_interconnects(model, funcNamesStack)
    # funcNamesStack.extend(gen_ics.params.funcNamesStack)

    logger.debug("funcNamesStack after ics:")
    logger.debug(funcNamesStack)

    (gen_bounds.common
     .set_params_for_bounds(model,
                            funcNamesStack, ics=gen_ics.params))
    # funcNamesStack.extend(gen_cent.params.funcNamesStack)

    logger.debug("funcNamesStack after bounds:")
    logger.debug(funcNamesStack)

    ### FOR remove duplicates:
    tmp = []
    for funcName in funcNamesStack:
        if funcName not in tmp:
            tmp.append(funcName)
    funcNamesStack = tmp

    # this solution:
    # funcNamesStack = list(set(funcNamesStack))
    # is depricated because set change order
    # each time.
    ### END FOR
    # END FOR

    logger.debug("funcNamesStack after set:")
    logger.debug(funcNamesStack)

    # for namesAndNumbers:
    gen_array.common.set_params_for_array(funcNamesStack)
    namesAndNumbers = gen_array.params.namesAndNumbers

    logger.debug("namesAndNumbers after array:")
    logger.debug(namesAndNumbers)

    # FOR functionMaps:
    functionMaps = {}
    (gen_cent.dom
     .set_params_for_dom_centrals(model,
                                  namesAndNumbers, functionMaps))
    # functionMaps.extend(gen_cent.dom.params.functionMaps)

    (gen_bounds.dom
     .set_params_for_dom_bounds(model,
                                namesAndNumbers, functionMaps))
    (gen_ics.dom
     .set_params_for_dom_interconnects(model,
                                       namesAndNumbers, functionMaps))
    # functionMaps.extend(gen_ics.params.functionMaps)

    # functionMaps.extend(gen_bounds.params.functionMaps)
    # END FOR

    out = str(functionMaps)
    # to_file(out, "from_test_domain_1d.txt")

    return((namesAndNumbers, functionMaps))

