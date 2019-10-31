'''
Created on Mar 2, 2017

@author: dglyzin
'''


import os
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.postproc.video')

# if using directly uncoment that:
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('postproc.plotter')
logger.setLevel(level=log_level)

import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

folder = "video"
sourcedir = currentdir.split(folder)[0]
logger.info("postproc dir:")
logger.info(sourcedir)
if sourcedir not in sys.path:
    sys.path += [sourcedir]

# from domainmodel.model import Model
from utils.binaryFileReader import readBinFile
from utils.binaryFileReader import readDomFile
from utils.binaryFileReader import getDomainProperties

from video.postprocessor import calcMinMax
from video.postprocessor import savePlots1D
from video.postprocessor import saveResults2D

from utils.fileUtils import getPlotValList


def decodePlotNumbers(plot_code):
    plot_code = plot_code/2
    plot_nums = []
    current_num = 0
    while plot_code > 0:
        if plot_code % 2 == 1:
            plot_nums.append(current_num)
        current_num = current_num+1
        plot_code = plot_code/2
    return plot_nums


def getDomAndJsonFile(dbin_pathNameExt):
    base = '-'.join(dbin_pathNameExt.split('-')[:-2])
    return base+".dom", base+".json"


def createPlots(dbin_pathNameExt, plot_code):
    # code into list
    plot_nums = decodePlotNumbers(plot_code)
    dom_pathNameExt, projectPathNameExt = getDomAndJsonFile(dbin_pathNameExt)
    projectDir, dbinNameExt = os.path.split(dbin_pathNameExt)
    _, projectNameExt = os.path.split(projectPathNameExt)
    projectName, _ = os.path.splitext(projectNameExt)

    # print("decoded: ", plot_nums)
    # print(dom_pathNameExt, projectPathNameExt)
    # model = Model()
    # model.loadFromFile(projectPathNameExt)
    
    info, cellSize, dx, dy, dz, dimension = readDomFile(dom_pathNameExt)
    
    out = getDomainProperties(info)
    countZ, countY, countX, offsetZ, offsetY, offsetX = out
    
    binTimeStr = dbin_pathNameExt.split('-')[-2]
         
    maxValue, minValue = calcMinMax(projectDir, [dbinNameExt], info,
                                    countZ, countY, countX,
                                    offsetZ, offsetY, offsetX, cellSize)
    saveText = 0
    for plotIdx in plot_nums:
        if dimension == 1:
            '''
            arg_list = [(projectDir, projectName, binFile,
                         info, countZ, countY, countX,
                         offsetZ, offsetY, offsetX, cellSize,
                         namesEquations,
                         plot['Value'], str(idx))
                        for idx, binFile in enumerate(plotFileLists[plotIdx])]
            logData = pool.map(getResults1D, arg_list)

            arg_list = [(projectDir, projectName,
                         [dataNum[1]], dataNum[0], countX,
                         offsetZ, offsetY, offsetX,
                         dataListMax, dataListMin, dx, dy,
                         str(Idx), plotIdx, picCount)
                        for Idx, dataNum in enumerate(logData)]
            '''
            savePlots1D(*[projectDir, projectName, dbinNameExt, info,
                          countZ, countY, countX,
                          offsetZ, offsetY, offsetX, cellSize,
                          maxValue, minValue, dx, dy,
                          "-current-" + binTimeStr, plotIdx, saveText])
        if dimension == 2:
            saveResults2D(*[projectDir, projectName, dbinNameExt, info,
                            countZ, countY, countX,
                            offsetZ, offsetY, offsetX, cellSize,
                            maxValue, minValue, dx, dy,
                            "-current-" + binTimeStr, plotIdx, saveText])
    
    
if __name__ == '__main__':

    desc = 'Creating pictures for a given draw binary file.'
    parser = argparse.ArgumentParser(description=desc, epilog="Have fun!")

    # mandatory argument, dbin file name
    parser.add_argument('dbin_pathNameExt', type=str,
                        help=("dbin file from which .dom"
                              + " and .json can be obtained too"))

    args = parser.parse_args()
    vals = getPlotValList([args.dbin_pathNameExt])
    createPlots(args.dbin_pathNameExt, vals[0])
