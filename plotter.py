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

def getDomAndJsonFile(dbin_fname):
    base = '-'.join(dbin_fname.split('-')[:-1])
    return base+".dom", base+".json"

def createPlots(dbin_fname, plot_code):
    #code into list
    plot_nums = decodePlotNumbers(plot_code)
    dom_fname, projectName = getDomAndJsonFile(dbin_fname)
    projectDir, dbinFile = os.path.split(dbin_fname) 
    
    print("decoded: ", plot_nums)
    print(dom_fname, projectName)
    model = Model()
    model.loadFromFile(projectName)
    
    
    info, cellSize, dx, dy, dz, dimension = readDomFile(dom_fname )
    
    countZ, countY, countX, offsetZ, offsetY, offsetX = getDomainProperties(info)
    
    binFileList = [dbinFile]
        
    maxValue, minValue = calcMinMax(projectDir, binFileList, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    saveText=0
    if dimension == 1:
        for idx, binFile in enumerate(binFileList):
            saveResults1D([projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx, saveText])
    if dimension == 2:
        for idx, binFile in enumerate(binFileList):
            saveResults2D([projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx, saveText] )
    
    
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating pictures for a given draw binary file.', epilog = "Have fun!")
    #mandatory argument, dbin file name
    parser.add_argument('dbin_fname', type = str, help = "dbin file from which .dom and .json can be obtained too")
    #mandatory argument, plot numbers needed for the file encoded in one integer 
    parser.add_argument('plot_code', type = int, help = "plots to build")
    args = parser.parse_args()
        
    createPlots(args.dbin_fname, args.plot_code)