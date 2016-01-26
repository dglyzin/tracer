'''
Created on Sep 30, 2015

@author: dglyzin
'''
import struct
import numpy as np
from domainmodel.enums import *

def readDomFile(fileName):
    #reading dom file
    dom = open(fileName, 'rb')    
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
    
    dimension, = struct.unpack('i', dom.read(4))
    
    cellSize, = struct.unpack('i', dom.read(4))
    haloSize, = struct.unpack('i', dom.read(4))
    
    solverNumber, = struct.unpack('i', dom.read(4))
    
    aTol, = struct.unpack('d', dom.read(8))
    rTol, = struct.unpack('d', dom.read(8))
    
    blockCount, = struct.unpack('i', dom.read(4))
    
    info = []
    for index in range(blockCount) :        
        node, = struct.unpack('i', dom.read(4))
        deviceType, = struct.unpack('i', dom.read(4))
        deviveNumber, = struct.unpack('i', dom.read(4))
        
        blockInfo = [0,0,0,1,1,1, node]
        
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
    
    return info, cellSize, dx, dy, dz, dimension

def combineBlocks(solution, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize):
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
        
    for j in range( len(info) ) :
        countZBlock = info[j][5]
        countYBlock = info[j][4]
        countXBlock = info[j][3]
    
        coordZBlock = info[j][2] - offsetZ
        coordYBlock = info[j][1] - offsetY
        coordXBlock = info[j][0] - offsetX
    
        total = countZBlock * countYBlock * countXBlock * cellSize
    
        blockData = solution[j]
        blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize)
        data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]
    
    return data

  
def readBinFile(fileName, info, countZ, countY, countX, offsetZ, offsetY, offsetX, cellSize):
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
    
    binF = open(fileName, 'rb')
    m253, = struct.unpack('b', binF.read(1))
    versionMajor, = struct.unpack('b', binF.read(1))
    versionMinor, = struct.unpack('b', binF.read(1))
    time, = struct.unpack('d', binF.read(8))
    timeStep, = struct.unpack('d', binF.read(8))

    for j in range( len(info) ) :
        countZBlock = info[j][5]
        countYBlock = info[j][4]
        countXBlock = info[j][3]
    
        coordZBlock = info[j][2] - offsetZ
        coordYBlock = info[j][1] - offsetY
        coordXBlock = info[j][0] - offsetX
    
        total = countZBlock * countYBlock * countXBlock * cellSize
    
        blockData = np.fromfile(binF, dtype=np.float64, count=total)
        blockData = blockData.reshape(countZBlock, countYBlock, countXBlock, cellSize);
        data[coordZBlock : coordZBlock + countZBlock, coordYBlock : coordYBlock + countYBlock, coordXBlock : coordXBlock + countXBlock, :] = blockData[:, :, :, :]
    binF.close()
    
    return data