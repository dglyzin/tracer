import numpy as np
from pandas import DataFrame

import logging


# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('tests.tester.filler_common')

# if using directly uncoment that:
'''
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('filler_common')
logger.setLevel(level=log_level)
'''


class Filler():

    def __init__(self, model):
        self.model = model

    def fillBinarySettings(self):
        model = self.model
        self.versionArr = np.zeros(3, dtype=np.uint8)
        self.versionArr[0] = 254
        self.versionArr[1] = 1
        self.versionArr[2] = 0

        self.timeAndStepArr = np.zeros(7, dtype=np.float64)
        self.timeAndStepArr[0] = model.solver.startTime
        self.timeAndStepArr[1] = model.solver.finishTime
        self.timeAndStepArr[2] = model.solver.timeStep
        self.timeAndStepArr[3] = model.solver.saveInterval
        self.timeAndStepArr[4] = model.grid.gridStepX
        self.timeAndStepArr[5] = model.grid.gridStepY
        self.timeAndStepArr[6] = model.grid.gridStepZ

        self.paramsArr = np.zeros(4, dtype=np.int32)
        self.paramsArr[0] = model.dimension
        self.paramsArr[1] = model.base.getCellSize()
        self.paramsArr[2] = model.base.getHaloSize()
        self.paramsArr[3] = model.solver.solverIndex
        
        self.toleranceArr = np.zeros(2, dtype=np.float64)
        self.toleranceArr[0] = model.solver.solverAtol
        self.toleranceArr[1] = model.solver.solverRtol

    def show(self, gout={}):
        
        '''Show all filled arrays in one place'''
        out = {}
        out['versionArr'] = {
            'array': self.versionArr,
            'frame': DataFrame([self.versionArr])}
        
        columns = ["startTime", "finishTime", "timeStep",
                   "saveInterval", "gsX", "gsY", "gsZ"]
        out['timeAndStepArr'] = {
            'array': self.timeAndStepArr,
            'frame': DataFrame([self.timeAndStepArr],
                               columns=columns)}
        
        columns = ['dim', 'cellSize', 'haloSize', 'solverIndex']
        out['paramsArr'] = {
            'array': self.paramsArr,
            'frame': DataFrame([self.paramsArr], columns=columns)}

        out['toleranceArr'] = {
            'array': self.toleranceArr,
            'frame': DataFrame([self.toleranceArr],
                               columns=['sAtol', 'sRtol'])}

        gout['common'] = out
        return(gout)

    def save_bin(self, domfile):
        self.versionArr.tofile(domfile)
        self.timeAndStepArr.tofile(domfile)
        self.paramsArr.tofile(domfile)
        self.toleranceArr.tofile(domfile)
