from gens.hs.env.definitions.def_main import Gen as GenDef
from gens.hs.env.initials.initials_main import Gen as GenInit
from gens.hs.env.params.params_main import Gen as GenParams
from gens.hs.env.centrals.cent_main import Gen as GenCent
from gens.hs.env.bounds.bounds_main import GenD1 as GenBounds
from gens.hs.env.ics.ics_main import GenD1 as GenIcs
from gens.hs.env.array.array_main import Gen as GenArr

from gens.hs.arrays_filler.filler_main import Filler

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_1d')
logger.setLevel(level=log_level)
'''


class GenD1():

    def __init__(self, net):

        self.net = net
        self.model = net.model
        self.delays = []

    def gen_cpp(self):

        '''
        DESCRIPTION:
        Generate cpp for 1d.

        Inputs:
        model either fileName of model obj.

        out will be in:
           self.cpp_out
           self.funcNamesStack
           self.namesAndNumbers
        '''
        model = self.model
 
        out = ""

        # out for definitions
        gen = GenDef()
        gen.common.set_params_for_definitions(model)
        out += gen.cpp_render.get_out_for_definitions()

        # out for initials:
        gen = GenInit()
        gen.cpp.set_params_for_initials(model)
        out += gen.cpp_render.get_out_for_initials()

        # out for params:
        gen = GenParams()
        gen.cpp.set_params_for_parameters(model)
        out += gen.cpp_render.get_out_for_parameters()

        funcNamesStack = []
        
        # out and funcNames for centrals:
        gen = GenCent()
        gen.common.set_params_for_centrals(model, funcNamesStack)
        out += gen.cpp_render.get_out_for_centrals()

        # out and funcNames for bounds:
        gen = GenBounds()
        gen.common.set_params_for_bounds(model, funcNamesStack)
        out += gen.cpp_render.get_out_for_bounds()

        # out and funcNames for ics:
        gen = GenIcs()
        gen.common.set_params_for_interconnects(model, funcNamesStack)
        out += gen.cpp_render.get_out_for_interconnects()

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

        # out and namesAndNumbers:
        gen = GenArr()
        gen.common.set_params_for_array(funcNamesStack)
        namesAndNumbers = gen.params.namesAndNumbers
        out += gen.cpp_render.get_out_for_array()

        # out = params.postprocessing(out)

        self.cpp_out = out
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers

    def gen_dom(self):
        '''
        DESCRIPTION:
        Generate funcs indexes and regions
        for 1d env.

        Inputs:
        model either fileName of model obj.

        out will be in:
           self.functionMaps
        '''
        model = self.model

        gen_cent = GenCent()
        gen_bounds = GenBounds()
        gen_ics = GenIcs()
        gen_array = GenArr()

        # FOR funcNameStack
        funcNamesStack = []

        gen_cent.common.set_params_for_centrals(model, funcNamesStack)
        logger.debug("funcNamesStack after cent:")
        logger.debug(funcNamesStack)

        gen_ics.common.set_params_for_interconnects(model, funcNamesStack)
        logger.debug("funcNamesStack after ics:")
        logger.debug(funcNamesStack)

        (gen_bounds.common
         .set_params_for_bounds(model,
                                funcNamesStack, ics=gen_ics.params))
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
        (gen_bounds.dom
         .set_params_for_dom_bounds(model,
                                    namesAndNumbers, functionMaps))
        (gen_ics.dom
         .set_params_for_dom_interconnects(model,
                                           namesAndNumbers, functionMaps))
        # functionMaps.extend(gen_bounds.params.functionMaps)
        # END FOR
        
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers
        self.functionMaps = functionMaps

    def gen_arrays(self):

        self.gen_dom()
        self.filler = Filler(self.model, self.functionMaps, self.delays)
        self.filler.fill_arrays()
        
        
