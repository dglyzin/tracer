# -*- coding: utf-8 -*-
'''
один входной аргумент - json файл, для которого уже выполнены расчеты
рядом с этим файлом будет создана папка с такимо же именем, в которую будут закачаны все 
вычисления, после чего будет для каждого файла нарисована картинка, а затем все 
склеено в видеофайл.
'''

import struct
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
from os import listdir

import multiprocessing as mp
from multiprocessing import Pool

import time
from fileUtils import getSortedBinFileList, defaultProjFname

import math


def savePng1D(filename, X, data, maxValue, minValue, currentTime, cellSize):
    figure = Figure()
    canvas = FigureCanvas(figure)
    
    t = str(currentTime)
    
    row = round(math.sqrt(cellSize))
    column = math.ceil(cellSize / row)
    
    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m, title=t)
        #figure.subplots_adjust(right=0.8)
        #cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap=cm.jet
        
        layer = data[0,0,:,i]
        axes.set_ylim(minValue, maxValue)
        axes.plot(layer)

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
    
    for i in range(cellSize):
        m = 100 * row + 10 * column + i + 1
        axes = figure.add_subplot(m, title=t)
        #figure.subplots_adjust(right=0.8)
        #cbaxes = figure.add_axes([0.85, 0.15, 0.05, 0.5])

        cmap=cm.jet
        
        layer = data[0,:,:,i]

        cb = axes.pcolormesh(X, Y, layer, vmin=minValue[i], vmax=maxValue[i])
        axes.axis([X.min(), X.max(), Y.min(), Y.max()])
        axes.set_aspect('equal')
        #figure.colorbar(cb, cax=cbaxes)
        
    ###    
    canvas.draw()
    figure.savefig(filename, format='png')            
    figure.clear()
    
    
    
    

def readDomFile(projectDir):
    #reading dom file
    dom = open(projectDir+"project.dom", 'rb')    
    m254, = struct.unpack('b', dom.read(1))
    versionMajor, = struct.unpack('b', dom.read(1))
    versionMinor, = struct.unpack('b', dom.read(1))
    
    startTime, = struct.unpack('d', dom.read(8))
    finishTime, = struct.unpack('d', dom.read(8))
    timeStep, = struct.unpack('d', dom.read(8))
    
    saveInterval, = struct.unpack('d', dom.read(8))
    
    dx, = struct.unpack('d', dom.read(8))
    dy, = struct.unpack('d', dom.read(8))
    dz, = struct.unpack('d', dom.read(8))
    
    cellSize, = struct.unpack('i', dom.read(4))
    haloSize, = struct.unpack('i', dom.read(4))
    
    solverNumber, = struct.unpack('i', dom.read(4))
    
    aTol, = struct.unpack('d', dom.read(8))
    rTol, = struct.unpack('d', dom.read(8))
    
    blockCount, = struct.unpack('i', dom.read(4))
    
    info = []
    for index in range(blockCount) :
        dimension, = struct.unpack('i', dom.read(4))
        node, = struct.unpack('i', dom.read(4))
        deviceType, = struct.unpack('i', dom.read(4))
        deviveNumber, = struct.unpack('i', dom.read(4))
        
        blockInfo = []
        blockInfo.append(0)
        blockInfo.append(0)
        blockInfo.append(0)
        blockInfo.append(1)
        blockInfo.append(1)
        blockInfo.append(1)
        
        for x in range(dimension) :
            coord, = struct.unpack('i', dom.read(4))
            blockInfo[x] = coord
        
        for x in range(dimension) :
            count, = struct.unpack('i', dom.read(4))
            blockInfo[x + 3] = count
        
        info.append(blockInfo)
        
        total = blockInfo[3] * blockInfo[4] * blockInfo[5]
        dom.read(2 * 2 * total)
    dom.close()
    
    return info, cellSize, dx, dy, dz


  
  
def calcAreaCharacteristics(info):
    minZ = 0
    maxZ = 0
    
    minY = 0
    maxY = 0
    
    minX = 0
    maxX = 0
    
    for i in range( len(info) ) :
        if info[i][2] < minZ :
            minZ = info[i][2]
    
        if info[i][2] + info[i][5] > maxZ :
            maxZ = info[i][2] + info[i][5]
    
        if info[i][1] < minY :
            minY = info[i][1]
    
        if info[i][1] + info[i][4] > maxY :
            maxY = info[i][1] + info[i][4]
    
        if info[i][0] < minX :
            minX = info[i][2]
    
        if info[i][0] + info[i][3] > maxX :
            maxX = info[i][0] + info[i][3]
    
    
    countZ = maxZ - minZ
    countY = maxY - minY
    countX = maxX - minX
    
    
    offsetZ = -minZ
    offsetY = -minY
    offsetX = -minX
    
    return countZ, countY, countX, offsetZ, offsetY, offsetX
  
  
  
  
  
def readBinFile(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize):
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
    
    bin = open(projectDir+"/"+binFile, 'rb')
    m253, = struct.unpack('b', bin.read(1))
    versionMajor, = struct.unpack('b', bin.read(1))
    versionMinor, = struct.unpack('b', bin.read(1))
    time, = struct.unpack('d', bin.read(8))

    for j in range( len(info) ) :
        countZBlock = info[j][5]
        countYBlock = info[j][4]
        countXBlock = info[j][3]
    
        coordZBlock = info[j][2] - offsetZ
        coordYBlock = info[j][1] - offsetY
        coordXBlock = info[j][0] - offsetX
    
        total = countZBlock * countYBlock * countXBlock * cellSize
    
        blockData = np.fromfile(bin, dtype=np.float64, count=total)
        blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize);
        data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]
    bin.close()
    
    return data
  
  
  
  
  
def calcMinMax(projectDir, binFileList, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize):
    maxValue = []#sys.float_info.min
    minValue = []#sys.float_info.max
    
    for i in range(cellSize):
        maxValue.append(sys.float_info.min)
        minValue.append(sys.float_info.max)
    
    for idx, binFile in enumerate(binFileList):
        data = readBinFile(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
        
        
        for i in range(cellSize):
            tmp = data[0,:,:,i]
       
            tmpMaxValue = np.max(tmp)
            tmpMinValue = np.min(tmp)
        
            if tmpMaxValue > maxValue[i]:
                maxValue[i] = tmpMaxValue
            
            if tmpMinValue < minValue[i]:
                minValue[i] = tmpMinValue
                
    print maxValue
    print minValue
           
    return maxValue, minValue
  
  
  



def createPng1D( (projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx) ):
   #for idx, binFile in enumerate(binFileList):
    data = readBinFile(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    
    xs = np.arange(0, countX)*dx
    ys = np.arange(0, countY)*dy


    X,Y = np.meshgrid(xs,ys)

    #plt.pcolormesh(X, Y, layer, vmin=minValue, vmax=maxValue)
    #plt.colorbar()
  
    filename = projectDir+"image-" + str(idx) + ".png"        
    #plt.savefig(filename, format='png')        
    #print 'save #', idx, binFile, "->", filename
    #plt.clf()
    
    t = binFile.split("-")[1]
    t = t.split(".bin")[0]
    
    savePng1D(filename, X, data, maxValue, minValue, t, cellSize)



  
def createPng2D( (projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx) ):
   #for idx, binFile in enumerate(binFileList):
    data = readBinFile(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    
    xs = np.arange(0, countX)*dx
    ys = np.arange(0, countY)*dy


    X,Y = np.meshgrid(xs,ys)

    #plt.pcolormesh(X, Y, layer, vmin=minValue, vmax=maxValue)
    #plt.colorbar()
  
    filename = projectDir+"image-" + str(idx) + ".png"        
    #plt.savefig(filename, format='png')        
    #print 'save #', idx, binFile, "->", filename
    #plt.clf()
    
    t = binFile.split("-")[1]
    t = t.split(".bin")[0]
    
    savePng2D(filename, X, Y, data, maxValue, minValue, t, cellSize)
        
        
        
        
def createVideoFile(projectDir):
    print "Creating video file:"
    command = "avconv -r 5 -i "+projectDir+"image-%d.png -b:v 1000k "+projectDir+"project.mp4"
    print command
    #PIPE = subprocess.PIPE
    #proc = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
    #proc.wait()
    subprocess.call(command, shell=True)
    print "Done" 

  
  
  
def createMovie(projectDir):
    info, cellSize, dx, dy, dz = readDomFile(projectDir)
    
    countZ, countY, countX, offsetZ, offsetY, offsetX = calcAreaCharacteristics(info)
    
    command = "rm " + projectDir + "image-*.png " + projectDir + "project.mp4"
    print command
    subprocess.call(command, shell=True)
    
    binFileList = getSortedBinFileList(projectDir, defaultProjFname)
    
    t1 = time.time()
    maxValue, minValue = calcMinMax(projectDir, binFileList, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize)
    t2 = time.time()
    #print "Расчет минимума / максимума: ", t2 - t1
    
    t1 = time.time()
    pool = mp.Pool(processes=16)
    #pool = mp.Semaphore(4)
    pool.map(createPng1D, [(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx) for idx, binFile in enumerate(binFileList)] )
    #pool.map(createPng2D, [(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx) for idx, binFile in enumerate(binFileList)] )
    #[pool.apply(createPng, args=(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx)) for idx, binFile in enumerate(binFileList)]
    t2 = time.time()
    
    
    #for idx, binFile in enumerate(binFileList):
    #    createPng(projectDir, binFile, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize, maxValue, minValue, dx, dy, idx)
    #print "Создание изображений: ", t2 - t1
    
    createVideoFile(projectDir)
  
  
  
if __name__ == "__main__":
    t1 = time.time()
    
    if len(sys.argv)<2:
        print "Please specify a project directory"
    else:
        projectDir = sys.argv[1]
        
        createMovie(projectDir)
        
    t2 = time.time()
    
    print "Общее время выполнения: ", t2 - t1