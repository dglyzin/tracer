from gens.hs.arrays_filler.filler_common import Filler as CommonFiller
from gens.hs.arrays_filler.blocks.blocks_filler_main import Filler as BlocksFiller
from gens.hs.arrays_filler.ics.ics_filler_main import Filler as IcsFiller
from gens.hs.arrays_filler.filler_plot import Filler as PlotFiller
from gens.hs.arrays_filler.filler_delays import Filler as DelaysFiller

import numpy as np
from pandas import DataFrame
from collections import OrderedDict

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.filler_main')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('filler_main')
logger.setLevel(level=log_level)
'''


class Filler():
    
    '''Transform envs to arrays.
    envs given by model
    ``functionMaps`` from dom generator
    delays.'''
    
    def __init__(self, model, functionMaps, funcNamesStack,
                 namesAndNumbers, delays=[]):

        self.model = model

        # for debug in dom.txt:
        self.functionMaps = functionMaps
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers

        self.fArray = CommonFiller(model)
        self.fBlocks = BlocksFiller(model, functionMaps)
        self.fIcs = IcsFiller(model)
        self.fPlot = PlotFiller(model)
        self.fDelays = DelaysFiller(model, delays)
        
    def fill_arrays(self):
        logger.info("filling arrays...")

        self.out_data = OrderedDict()
        self.fArray.fillBinarySettings()
        self.fArray.show(gout=self.out_data)

        self.fDelays.fill_delays()
        self.fDelays.show(gout=self.out_data)

        # this will only work if saveFuncs was called
        # and self.functionMaps are filled
        self.fBlocks.fillBinaryBlocks()
        self.fBlocks.plotter.show(gout=self.out_data)

        self.fIcs.fillBinaryInterconnects()
        self.fIcs.plotter.show(gout=self.out_data)
        
        self.fPlot.fillBinaryPlots()
        self.fPlot.show(gout=self.out_data)

    def show(self):

        '''only after
        self.fill_arrays'''

        out = ""
        for e in self.out_data:
            out += '\n' + e + '\n'
            for p in self.out_data[e]:
                out += p + '\n'
                if p in ('blockInitFuncArrList',
                         'blockCompFuncArrList'):
                    for a in self.out_data[e][p]['array']:
                        out += str(a) + '\n'
                else:
                    out += str(self.out_data[e][p]['frame']) + '\n'
        return(out)

    def save_txt(self, fileName):

        '''only after
        ``self.fill_arrays``'''

        out = self.show()
        out += "\n\n functionMaps: \n"
        out += str(self.functionMaps)
        out += "\n\n funcNamesStack: \n"
        out += str(self.funcNamesStack)
        out += "\n\n namesAndNumbers: \n"
        out += str(self.namesAndNumbers)

        with open(fileName, 'w') as f:
            f.write(out)

    def save_bin(self, fileName, delays=[]):

        '''only after
        ``self.fill_arrays``'''

        logger.info("saving domain...")

        # saving
        with open(fileName, "wb") as domfile:

            #1. Save common settings
            self.fArray.save_bin(domfile)

            #1.1. delays 
            self.fDelays.save_bin(domfile)

            #2. Save blocks
            self.fBlocks.save_bin(domfile)

            #3. Save interconnects
            self.fIcs.save_bin(domfile)

            # 4. Save plot and reuslts:
            self.fPlot.save_bin(domfile)
