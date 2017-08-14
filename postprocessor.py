# -*- coding: utf-8 -*-
'''
один входной аргумент - json файл, для которого уже выполнены расчеты
рядом с этим файлом будет создана папка с такимо же именем, в которую будут закачаны все 
вычисления, после чего будет для каждого файла нарисована картинка, а затем все 
склеено в видеофайл.
'''

import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
import sys
import subprocess

from domainmodel.model import Model
import getpass
#import paramiko, socket
import os
from os import listdir
import json

import multiprocessing as mp
from multiprocessing import Pool

import time
from fileUtils import getSortedDrawBinFileList, drawExtension, defaultGeomExt, getPlotValList

import math
from domainmodel.binaryFileReader import readBinFile, readDomFile, getDomainProperties

from mpl_toolkits.axes_grid1 import make_axes_locatable


def savePng1D(filename, X, data, maxValue, minValue, currentTime, cellSize):
    figure = Figure()
    canvas = FigureCanvas(figure)
    
    t = str(currentTime)
    
    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)
    
    figure.suptitle(t)
    
    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m)
        #figure.subplots_adjust(right=0.8)
        #cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap=cm.jet
        
        amp = maxValue[i] - minValue[i]
        
        minV = minValue[i] - amp/10
        maxV = maxValue[i] + amp/10
        
        layer = data[0,0,:,i]
        axes.set_ylim(minV, maxV)
        axes.set_xlim(X.min(), X.max())
        #axes.axis([X.min(), X.max(), minValue, maxValue])
        #a = np.arange(X.min(), X.max(), (X.max() - X.min()) / layer.size)
        #print a.size, layer.size
        axes.plot(X, layer)

        #cb = axes.pcolormesh(X, Y, layer, vmin=minValue[i], vmax=maxValue[i])
        #axes.axis([X.min(), X.max(), minValue, maxValue])
        #figure.colorbar(cb, cax=cbaxes)
        
    ###
    canvas.draw()
    figure.savefig(filename, format='png')            
    figure.clear()


def savePng2D(filename, X, Y, data, maxValue, minValue, currentTime, cellSize):
    figure = Figure()
    canvas = FigureCanvas(figure)
    
    t = str(currentTime)
    
    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)
    
    figure.suptitle(t)
    
    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m)
        figure.subplots_adjust(right=0.8)
        #cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap=cm.jet
        
        layer = data[0,:,:,i]

        cb = axes.pcolormesh(X, Y, layer, vmin=minValue[i], vmax=maxValue[i])
        
        axes.axis([X.min(), X.max(), Y.min(), Y.max()])
        axes.set_aspect('equal')
        figure.colorbar(cb, ax=axes, fraction=0.046, pad=0.04)
        
    ###
    if cellSize > 1:
        figure.tight_layout()
        
    canvas.draw()
    figure.savefig(filename, format='png')            
    figure.clear()
    
    
def saveTxt2D(filename, X, Y, data, maxValue, minValue, currentTime, cellSize):
    txtFile = open(filename,"w")
    
    t = str(currentTime)
    
    _, m,n, _ = data.shape
    
    line = "Y X values \n"
    
    txtFile.write(line)
    
    for i in range(m):
        for j in range(n):
            line = "{0} {1} ".format(str(Y[i,j]), str(X[i,j]) )
            for k in range(cellSize):
                line = line + str(data[0,i,j,k]) + " "      
            line = line+"\n"
            txtFile.write(line)                        
    txtFile.close()  
 
    
def calcMinMax(projectDir, binFileList, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize):
    maxValue = []#sys.float_info.min
    minValue = []#sys.float_info.max
    
    for i in range(cellSize):
        maxValue.append(sys.float_info.min)
        minValue.append(sys.float_info.max)
    
    for idx, binFile in enumerate(binFileList):
        data = readBinFile(projectDir+"/"+binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
        
        
        for i in range(cellSize):
            tmp = data[0,:,:,i]
       
            tmpMaxValue = np.max(tmp)
            tmpMinValue = np.min(tmp)
        
            if tmpMaxValue > maxValue[i]:
                maxValue[i] = tmpMaxValue
            
            if tmpMinValue < minValue[i]:
                minValue[i] = tmpMinValue
                
        
    for i in range(cellSize):
        if (maxValue[i] - minValue[i]) < 1e-300:
            maxValue[i] = maxValue[i] + 1
            minValue[i] = minValue[i] - 1
                
    print maxValue
    print minValue
           
    return maxValue, minValue
  
  
  



def savePlots1D( (projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, postfix, plotIdx, saveText) ):
    #for idx, binFile in enumerate(binFileList):
    data = readBinFile(projectDir+"/"+binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    
    xs = np.arange(0, countX)*dx
    #ys = np.arange(0, countY)*dy
    #print "xs", xs

    #X,Y = np.meshgrid(xs,ys)
    #print "X", X

    #plt.pcolormesh(X, Y, layer, vmin=minValue, vmax=maxValue)
    #plt.colorbar()
  
    filename = os.path.join(projectDir,projectName+"-plot"+str(plotIdx) + postfix + ".png")        
    #plt.savefig(filename, format='png')        
    #print 'save #', idx, binFile, "->", filename
    #plt.clf()
    
    t = binFile.split("-")[-2]
    #t = t.split(drawExtension)[0]
    savePng1D(filename, xs, data, maxValue, minValue, t, cellSize)
    #print("produced png: "+ filename)
    return "produced png: "+ filename


def getResults1D((projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, resultExpression, idx)):
    '''
        returns time and requested value from state file binfile  
    '''
    dictfunc = {u'U': 0, u'V': 1}
    data = readBinFile(projectDir+"/"+binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    #xs = np.arange(0, countX)*dx
    if resultExpression in dictfunc:
        idx = dictfunc[resultExpression]
    else:
        idx = 0

    res = data[0,0,:,idx]
    #filename = os.path.join(projectDir,projectName+"-res"+str(resIdx) + postfix + ".txt")        
    
    t = binFile.split("-")[-2]
        
    #t = t.split(drawExtension)[0]
    #with open(filename, "w") as f:
    #    f.write(t)
    #savePng1D(filename, xs, data, maxValue, minValue, t, cellSize)
    #print("produced png: "+ filename)
    return t, res#"produced text result: "+ filename

def createResultFile(projectDir, projectName, resIdx, resLog):
    print "Creating out file:"
    
    outfileNamePath = projectDir+projectName+"-res"+str(resIdx)+".out"
    
    with open(outfileNamePath, "w") as f:
        for time, item in resLog:
            f.write(str(time)+": "+ str(item)+"\n")
    
    
    
    #infileNamePath  = projectDir+projectName+"-plot"+str(resIdx)+"-final-%d.png"
    
    #PIPE = subprocess.PIPE
    #proc = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
    #proc.wait()
    #subprocess.call(command, shell=True)
    print "Done" 


  
def saveResults2D(projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, postfix, plotIdx, saveText):
    #for idx, binFile in enumerate(binFileList):
    data = readBinFile(projectDir+"/"+binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    
    xs = np.arange(0, countX)*dx
    ys = np.arange(0, countY)*dy


    X,Y = np.meshgrid(xs,ys)

    #plt.pcolormesh(X, Y, layer, vmin=minValue, vmax=maxValue)
    #plt.colorbar()
  
    filename = os.path.join(projectDir, projectName+"-plot"+str(plotIdx)+postfix + ".png")        
    #plt.savefig(filename, format='png')        
    #print 'save #', idx, binFile, "->", filename
    #plt.clf()
    
    t = binFile.split("-")[1]
    t = t.split(drawExtension)[0]
    
    savePng2D(filename, X, Y, data, maxValue, minValue, t, cellSize)
    #if saveText:
    #    filenameTxt = projectDir+projectName+"-txtFile-" + str(idx) + ".txt"        
    #    saveTxt2D(filenameTxt, X, Y, data, maxValue, minValue, t, cellSize)

    #print("produced png: "+ filename)
    return "produced png: "+ filename
    
        
def createVideoFile(projectDir, projectName, plotIdx):
    print "Creating video file:"
    command = "avconv -r 5 -loglevel panic -i "+projectDir+projectName+"-plot"+str(plotIdx)+"-final-%d.png -b:v 1000k "+projectDir+projectName+"-plot"+str(plotIdx)+".mp4"
    print command
    #PIPE = subprocess.PIPE
    #proc = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
    #proc.wait()
    subprocess.call(command, shell=True)
    print "Done" 

def plot_contains(idx, val):
    plotcode = 1 << (idx+1)
    return val&plotcode  
  
def getBinFilesByPlot(binFileList, plotValList, plotCount):  
    #separate binFileList into sublists according to plotValList    
    result = []
    for _ in range(plotCount):
        result.append([])
    for fileName, plotVal in zip(binFileList, plotValList):
        for plotIdx in range(plotCount):
            if plot_contains(plotIdx, plotVal):
                result[plotIdx].append(fileName)
    return result
  
  
def createMovie(projectDir, projectName):    
    saveText = False
    
    
    info, cellSize, dx, dy, dz, dimension = readDomFile(os.path.join(projectDir, projectName + defaultGeomExt) )
    
    countZ, countY, countX, offsetZ, offsetY, offsetX = getDomainProperties(info)
    
    command = "rm " + projectDir + projectName + "-final-*.png " + projectDir + projectName + "-plot*.mp4" + projectDir + projectName + "-res*.txt" + projectDir + projectName + "-res*.out"
    print command
    subprocess.call(command, shell=True)
    
    binFileList = getSortedDrawBinFileList(projectDir, projectName)
    plotValList = getPlotValList(binFileList)
    #print plotValList
    
    model = Model()
    model.loadFromFile(os.path.join(projectDir, projectName + '.json'))
    plotCount = len(model.plots)
    resultList = model.results
    resCount = len(model.results)
    plotFileLists=getBinFilesByPlot(binFileList, plotValList, plotCount+resCount)
    #print plotFileLists

    for plotIdx in range(plotCount):    
        #t1 = time.time()
        maxValue, minValue = calcMinMax(projectDir, plotFileLists[plotIdx], info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
        #t2 = time.time()
        #print "Расчет минимума / максимума: ", t2 - t1
    
        pool = mp.Pool(processes=16)
        saveResultFunc = savePlots1D
        if dimension == 1:
            saveResultFunc = savePlots1D
        if dimension == 2:
            saveResultFunc = saveResults2D
            
        log = pool.map(saveResultFunc, [(projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ,
                                         offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, "-final-" + str(idx),
                                         plotIdx, saveText) for idx, binFile in enumerate(plotFileLists[plotIdx]) ] )
        
        for element in log:
            print element
    
        createVideoFile(projectDir, projectName,plotIdx)

    #U and V
    #TODO get result all list U or V
    resIdx = 0
    #print('aaaa ',resultlistname)
    for resultItem in resultList:
        pool = mp.Pool(processes=16)
        resuls = pool.map(getResults1D, [(projectDir, projectName, binFile, info, countZ, countY, countX, offsetZ,
                                                offsetY, offsetX, cellSize, resultItem['Value'],
                                              str(idx)) for idx, binFile in enumerate(plotFileLists[plotCount + resIdx])])
        print('sks',projectDir, resultItem)
        createResultFile(projectDir, projectName, resIdx, resuls)
        resIdx += 1

  
if __name__ == "__main__":
    t1 = time.time()
    
    parser = argparse.ArgumentParser(description='Creating pictures and a movie for a given folder.', epilog = "Have fun!")
    #mandatory argument, project folder
    parser.add_argument('projectDir', type = str, help = "local folder to process")
    #mandatory argument, project name without extension
    parser.add_argument('projectName', type = str, help = "project name without extension")
    args = parser.parse_args()
        
    createMovie(args.projectDir, args.projectName)
        
    t2 = time.time()
    
    print "Postprocessor running time: ", t2 - t1
