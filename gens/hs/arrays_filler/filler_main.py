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
    delays.
    
    :doc:`overview <blocks>`
    :doc:`overview <../../../../../overview>`
    :doc:`overview <../../../../../../overview>`
    :doc:`overview <../../overview>`
    :doc:`overview <../../../overview>`

    Binary format:
    
    ::

        ##Domain file format for hybriddomain project
        ##Version 1 domain (.dom)

        # Domain geometry
        ##!  uint8: 254
        ##!  uint8: file format version major
        ##!  uint8: file format version minor

        ##!  3*float64: StartTime, FinishTime, Initial timestep
        ##!  float64: save interval
        ##!  3* float64: dx, dy, dz
        ##!  int32 dimension Db (can be 1,2 or 3) 
        ##!  int32 Cell Size
        ##!  int32 Halo Size
        ##!  int32 Solver number (0=Euler, 1= RK4, etc,  see solver.h)
        ##!  2* float64: Solver absolute and relative tolerance

        ##!  1*int: problem type (0 - ordinary, 1 - delay)
        ###  if problem type == 1
        ##!  1*int number of delays N_D
        ##!  N_D*float64 delay values
        ##!  uint64 S_N number of states that can be stored in memory
        ###  endif

        ### blocks 
        ##!  int32: number of blocks N_B
        ### following are N_B 1-2-3d blocks one by one
        ### BEGINNING OF BLOCK 
        ##!  int32 computation node
        ##!  int32 computation device type
        ##!  int32 computation device number
        ##!  Db*int32: offset x, y, z (in number of grid steps) 
        ##!  Db*int32: xc, yc, and zc number of grid steps \
             in this block, total=xc*yc*zc
        ### properties of every volume
        ##!  total*uint16: init function number
        ##!  total*uint16: computation function number 
        ### END OF BLOCK

        ### Interconnects 
        ##!  int32: number of interconnects N_I
        ### following are N_I interconnects one by one
        ### BEGINNING OF IC
        ##!  int32 dimension I_d (can be 0,1,2)
        ##!  I_d*int32 interconnect length
        ##!  int32 source block
        ##!  int32 destination block
        ##!  int32 source side (0-5)
        ##!  int32 destination side (0-5)
        ##!  I_d*int32 source offset
        ##!  I_d*int32 destination offset
        ### END OF IC

        ### Plot and text results config
        ##!  int32: number of plots and results N_P
        ##!  N_P * float64 interval values
        ### End of plot config

        ===============================================
        ## State file format for draw(*.dbin)
        ##!  uint8: 253
        ##!  uint8: file format version major
        ##!  uint8: file format version minor

        ##!  float64 current time 
        ##!  float64 current timestep
        ###  following is the N_B  blocks one by one
        ###  BEGINNING OF THE BLOCK##!   
        ##!   total*cellsize*float64: state 
        ###  END OF THE BLOCK

        ===============================================
        ## State file format for load (ODE) (*.lbin)
        ##!  uint8: 253
        ##!  uint8: file format version major
        ##!  uint8: file format version minor

        ##!  float64 current time 
        ##!  float64 current timestep
        ###  following is the N_B  blocks one by one
        ###  BEGINNING OF THE BLOCK##!   
        ##!  total*cellsize*float64: state
        ###  END OF THE BLOCK

        ===============================================
        ## State file format for load (DDE) (*.lbin)
        ##!  uint8: 253
        ##!  uint8: file format version major
        ##!  uint8: file format version minor

        ##!  float64 current time 
        ##!  float64 current timestep

        ##!  int32 currentStateNumber
        ##!  int32*delaycount delay state indices
        ##!  number of useful states*float64 state timestamps
        ###  following is the N_B  blocks one by one
        ###  BEGINNING OF THE BLOCK 
        ##!  number of useful states*state size*float64
        ###  END OF THE BLOCK

        ###  following is the N_B  blocks one by one
        ###  BEGINNING OF THE BLOCK##!   
        ##!   total*cellsize*float64: state 
        ###  END OF THE BLOCK

    Порядок функций:

    1. центральная функция
    2. Далее угловые функции
    3. далее в порядке границ 0-1-2-3 для каждой границы 
    4. 1- условие по умолчанию
    5. 2- н условия пользователя в том порядке 

    1d::

        гало = 1
        [1 0 0 0 0 0 0 0 0 2]

        гало = 2
        [1 2 0 0 0 0 0 0 3 4]

    2d ось x по горизонтали, ось y по вертикали::

        гало = 1
        [[1 5 5 5 6 5 6 6 6  2]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [9 0 0 0 0 0 0 0 0 10]
         [8 0 0 0 0 0 0 0 0 10]
         [8 0 0 0 0 0 0 0 0 10]
         [8 0 0 0 0 0 0 0 0 10]
         [3 7 7 7 7 7 7 7 7 4]

        гало = 2
        [[ 1  2  3  3  3  3  3  3  4  5]
         [ 6  7  8  8  8  8  8  8  9 10]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [11 12  0  0  0  0  0  0 13 14]
         [15 16 17 17 17 17 17 17 18 19]
         [20 21 22 22 22 22 22 22 23 24]]

    Border conditions:

    Краевое условие типа Неймана переписывает касающиеся
    его клетки (длина задана пользователем, ширина равна гало). <br>
    Если это условие накладывается на угол, то угол не переписывается.
    <br/>
    Если одно и то же краевое условие Неймана встречается несколько
    раз в границах, то каждый экземпляр имеет свой собственный номер
    и свою функцию, т.к. функции на разных границах обычно  различаются.

    Краевое условие типа Дирихле на всем своем протяжении переписывает
    одну и ту же функцию вычисления производной.
    Для констант это просто возврат нуля, для функций,
    зависящих от времени - вычисленная пользователем произовдная.
    Все регионы, соответствующие одному условию Дирихле,
    помечаются одной функцией в том порядке, в котором
 
    Краевое условие типа Дирихле требует изменения
    начального условия в касающихся его клетках.

    Итоговый порядок функций на примере гало=1:
     0..8 - Нейманы по умолчанию

    Каждая вычислительная функция принимает на вход список
    границ блока ``double**`` в том порядке, в котором появились
    входящие в этот блок интерконнекты.
  
    Example for 1d (Brusselator1d):
    
    ::

        common
        versionArr
             0  1  2
        0  254  1  0
        timeAndStepArr
           startTime  finishTime  timeStep  saveInterval    gsX  gsY  gsZ
        0        0.0        60.0   0.00001           0.1  0.001  1.0  1.0
        paramsArr
           dim  cellSize  haloSize  solverIndex
        0    1         2         1            0
        toleranceArr
           sAtol  sRtol
        0  0.001  0.001

        delays
        problemTypeArr
           0
        0  0

        blocks
        blockCountArr
           0
        0  4
        blockPropArrList
           nodeIdx  DeviceType  DeviceIdx  cellOffsetX  cellCountX
        0        0           0          0            0        1001
        1        0           0          0            0        1001
        2        0           0          0            0        1001
        3        0           0          0            0        1001
        blockInitFuncArrList
        [0 0 0 ..., 0 0 0]
        [0 0 0 ..., 0 0 0]
        [0 0 0 ..., 0 0 0]
        [0 0 0 ..., 0 0 0]
        blockCompFuncArrList
        [2 0 0 ..., 0 0 1]
        [1 0 0 ..., 0 0 2]
        [1 0 0 ..., 0 0 2]
        [1 0 0 ..., 0 0 2]

        ics
        icCountArr
           0
        0  8
        icList
           icDim  block_2  block_1  block2Side  block1Side
        0      0        0        1           1           0
        1      0        1        0           0           1
        2      0        1        2           1           0
        3      0        2        1           0           1
        4      0        2        3           1           0
        5      0        3        2           0           1
        6      0        1        3           0           1
        7      0        3        1           1           0

        plotAndRes
        plotAndResCountArr
           0
        0  2
        plotAndResPeriodsArr
             0    1
        0  0.1  0.1

        functionMaps:

        {0:
         {'center_default': 0,
          'side1': 1, 'center': [], 'side0': 2},
         1: {'center_default': 0, 'side1': 2, 'center': [], 'side0': 1},
         2: {'center_default': 0, 'side1': 2, 'center': [], 'side0': 1},
         3: {'center_default': 0, 'side1': 2, 'center': [], 'side0': 1}}

        funcNamesStack:

        ['Block0CentralFunction_Eqn0',
         'Block1CentralFunction_Eqn0',
         'Block2CentralFunction_Eqn0',
         'Block3CentralFunction_Eqn0',
         'Block0Interconnect__Side1_Eqn0',
         'Block1Interconnect__Side0_Eqn0',
         'Block1Interconnect__Side1_Eqn0',
         'Block2Interconnect__Side0_Eqn0',
         'Block2Interconnect__Side1_Eqn0',
         'Block3Interconnect__Side0_Eqn0',
         'Block3Interconnect__Side1_Eqn0',
         'Block0DefaultNeumann__side0__Eqn0']

        namesAndNumbers:

        {0: ['Block0CentralFunction_Eqn0',
             'Block0Interconnect__Side1_Eqn0',
             'Block0DefaultNeumann__side0__Eqn0'],
         1: ['Block1CentralFunction_Eqn0',
             'Block1Interconnect__Side0_Eqn0', 
             'Block1Interconnect__Side1_Eqn0'],
         2: ['Block2CentralFunction_Eqn0',
             'Block2Interconnect__Side0_Eqn0',
             'Block2Interconnect__Side1_Eqn0'],
         3: ['Block3CentralFunction_Eqn0',
             'Block3Interconnect__Side0_Eqn0',
             'Block3Interconnect__Side1_Eqn0']}
    '''

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
