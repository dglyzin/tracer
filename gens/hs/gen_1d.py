from gens.hs.postproc.postproc_main import Postproc

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

        self.postproc = Postproc(self)

        self.model = net.model
        self.delays = []

    def gen_cpp(self):

        '''
        DESCRIPTION::

        Generate cpp for 1d.

        out will be in::

           ``self.cpp_out``
           ``self.funcNamesStack``
           ``self.namesAndNumbers``
        '''
        model = self.model
 
        out = ""

        # out for definitions
        gen_def = GenDef()
        gen_def.common.set_params_for_definitions(model)

        # out for initials:
        gen_init = GenInit()
        gen_init.cpp.set_params_for_initials(model)

        # out for params:
        gen_params = GenParams()
        gen_params.cpp.set_params_for_parameters(model)

        funcNamesStack = []
        
        # out and funcNames for centrals:
        gen_cent = GenCent()
        gen_cent.common.set_params_for_centrals(model, funcNamesStack)

        # out and funcNames for bounds:
        gen_bounds = GenBounds()
        gen_bounds.common.set_params_for_bounds(model, funcNamesStack)

        # out and funcNames for ics:
        gen_ics = GenIcs()
        gen_ics.common.set_params_for_interconnects(model, funcNamesStack)

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
        gen_arr = GenArr()
        gen_arr.common.set_params_for_array(funcNamesStack)
        namesAndNumbers = gen_arr.params.namesAndNumbers

        # for postproc:
        delays = self.postproc.postporc_delays([gen_cent,
                                                gen_bounds, gen_ics])
        logger.info("delays:")
        logger.info(delays)
        sizes_delays = dict([(len(delays[var]), delays[var])
                             for var in delays])
        try:
            max_delays_seq = sizes_delays[max(sizes_delays)]
            self.delays = max_delays_seq
            logger.info("max_delays_seq:")
            logger.info(max_delays_seq)
        except ValueError:
            self.delays = []

        out += gen_def.cpp_render.get_out_for_definitions()
        out += gen_init.cpp_render.get_out_for_initials()
        out += gen_params.cpp_render.get_out_for_parameters()
        out += gen_cent.cpp_render.get_out_for_centrals()
        out += gen_bounds.cpp_render.get_out_for_bounds()
        out += gen_ics.cpp_render.get_out_for_interconnects()
        out += gen_arr.cpp_render.get_out_for_array()

        self.cpp_out = out
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers

    def gen_dom(self):
        '''
        DESCRIPTION::

        Generate funcs indexes and regions
        for 1d env.

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
        
        
