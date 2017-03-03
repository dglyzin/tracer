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

from domainmodel.model import Model
from domainmodel.binaryFileReader import readBinFile, readDomFile, getDomainProperties
from postprocessor import calcMinMax, saveResults1D, saveResults2D
from fileUtils import getPlotValList

def decodePlotNumbers(plot_code):
    plot_code = plot_code/2
    plot_nums = []
    current_num = 0
    while plot_code>0:
        if plot_code%2 == 1:
            plot_nums.append(current_num)
        current_num = current_num+1
        plot_code = plot_code/2
    return plot_nums

def getDomAndJsonFile(dbin_pathNameExt):
    base = '-'.join(dbin_pathNameExt.split('-')[:-2])
    return base+".dom", base+".json"

def createPlots(dbin_pathNameExt, plot_code):
    #code into list
    plot_nums = decodePlotNumbers(plot_code)
    dom_pathNameExt, projectPathNameExt = getDomAndJsonFile(dbin_pathNameExt)
    projectDir, dbinNameExt = os.path.split(dbin_pathNameExt) 
    _, projectNameExt = os.path.split(projectPathNameExt)
    projectName, _ = os.path.splitext(projectNameExt)
    #print("decoded: ", plot_nums)
    #print(dom_pathNameExt, projectPathNameExt)
    model = Model()
    model.loadFromFile(projectPathNameExt)
    
    
    info, cellSize, dx, dy, dz, dimension = readDomFile(dom_pathNameExt )
    
    countZ, countY, countX, offsetZ, offsetY, offsetX = getDomainProperties(info)
    
    binTimeStr = dbin_pathNameExt.split('-')[-2]
         
    maxValue, minValue = calcMinMax(projectDir, [dbinNameExt], info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    saveText=0
    for plotIdx in plot_nums:    
        if dimension == 1:        
            saveResults1D([projectDir, projectName, dbinNameExt, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, "-current-" + binTimeStr, plotIdx, saveText])
        if dimension == 2:        
            saveResults2D([projectDir, projectName, dbinNameExt, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, "-current-" + binTimeStr, plotIdx, saveText] )
    
    
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating pictures for a given draw binary file.', epilog = "Have fun!")
    #mandatory argument, dbin file name
    parser.add_argument('dbin_pathNameExt', type = str, help = "dbin file from which .dom and .json can be obtained too")
    
    args = parser.parse_args()    
    vals = getPlotValList([args.dbin_pathNameExt])    
    createPlots(args.dbin_pathNameExt, vals[0])
    
    
    
    