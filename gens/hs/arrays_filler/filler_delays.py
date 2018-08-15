import numpy as np
from pandas import DataFrame
from collections import OrderedDict


class Filler():
    def __init__(self, model, delays):
        self.model = model
        self.delays = delays

    def fill_delays(self):

        '''Fill
        self.problemTypeArr
        
        if len(delays) > 0:
           self.problemDelaysLen
           self.problemDelaysList
           self.maxStatesCountArr'''

        delays = self.delays

        if len(delays) == 0:
            # without delays
            self.problemTypeArr = np.zeros(1, dtype=np.int32)
        else:
            # delays
            self.problemTypeArr = np.ones(1, dtype=np.int32)

            # delays length
            self.problemDelaysLen = np.array([len(delays)], dtype=np.int32)

            # delays list
            self.problemDelaysList = np.array(delays, dtype=np.float64)

            # also we have to provide the number of states
            # that can be stored in memory
            maxStatesCount = self.model.device.getMaxStatesCount()
            self.maxStatesCountArr = np.array([maxStatesCount],
                                              dtype=np.uint64)

    def show(self, gout={}):
        out = OrderedDict()
        out['problemTypeArr'] = {
            'array': self.problemTypeArr,
            'frame': DataFrame([self.problemTypeArr])}

        if len(self.delays) > 0:
            out['problemDelaysLen'] = {
                'array': self.problemDelaysLen,
                'frame': DataFrame([self.problemDelaysLen])}

            out['problemDelaysList'] = {
                'array': self.problemDelaysList,
                'frame': DataFrame([self.problemDelaysList])}

            out['maxStatesCountArr'] = {
                'array': self.maxStatesCountArr,
                'frame': DataFrame([self.maxStatesCountArr])}

        gout['delays'] = out
        return(gout)

    def save_bin(self, domfile):
        delays = self.delays

        if len(delays) == 0:
            # without delays
            self.problemTypeArr.tofile(domfile)
        else:
            # delays
            self.problemTypeArr.tofile(domfile)

            # delays length
            self.problemDelaysLen.tofile(domfile)

            # delays list
            self.problemDelaysList.tofile(domfile)

            # also we have to provide the number of states
            # that can be stored in memory
            self.maxStatesCountArr.tofile(domfile)
