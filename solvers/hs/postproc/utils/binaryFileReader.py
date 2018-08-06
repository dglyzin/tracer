'''
Created on Sep 30, 2015

@author: dglyzin
'''
import struct
import numpy as np
from utils.enums import *

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.binaryFileReader')

# if using directly uncoment that:
# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('binaryFileReader')
logger.setLevel(level=log_level)


def readDomFile(fileName):
    # reading dom file
    try:
        dom = open(fileName, 'rb')
    except:
        logger.error("Can not open file {}".format(fileName))
        return   
        
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
    
    problemType, = struct.unpack('i', dom.read(4))
    if problemType == 1 :
        delayCount, = struct.unpack('i', dom.read(4))
        for i in range(0, delayCount):
            struct.unpack('d', dom.read(8))
        struct.unpack('Q', dom.read(8))
    
    blockCount, = struct.unpack('i', dom.read(4))
    
    info = []
    for index in range(blockCount):        
        node, = struct.unpack('i', dom.read(4))
        deviceType, = struct.unpack('i', dom.read(4))
        deviveNumber, = struct.unpack('i', dom.read(4))
        
        blockInfo = [0, 0, 0, 1, 1, 1, node]
        
        for x in range(dimension):
            coord, = struct.unpack('i', dom.read(4))
            blockInfo[x] = coord
        
        for x in range(dimension):
            count, = struct.unpack('i', dom.read(4))
            blockInfo[x + 3] = count
        
        info.append(blockInfo)
        
        total = blockInfo[3] * blockInfo[4] * blockInfo[5]
        dom.read(2 * 2 * total)
    dom.close()
    
    return info, cellSize, dx, dy, dz, dimension


def combineBlocks(solution, info,
                  countZ, countY, countX,
                  offsetZ, offsetY, offsetX,
                  cellSize):
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
        
    for j in range(len(info)):
        countZBlock = info[j][5]
        countYBlock = info[j][4]
        countXBlock = info[j][3]
    
        coordZBlock = info[j][2] - offsetZ
        coordYBlock = info[j][1] - offsetY
        coordXBlock = info[j][0] - offsetX
    
        total = countZBlock * countYBlock * countXBlock * cellSize
    
        blockData = solution[j]
        blockData = blockData.reshape(countZBlock, countYBlock, countXBlock,
                                      cellSize)

        data[coordZBlock: coordZBlock + countZBlock,
             coordYBlock: coordYBlock + countYBlock,
             coordXBlock: coordXBlock + countXBlock, :] = blockData[:, :, :, :]
    
    return data

  
def readBinFile(fileName, info,
                countZ, countY, countX,
                offsetZ, offsetY, offsetX,
                cellSize):
    data = np.zeros((countZ, countY, countX, cellSize), dtype=np.float64)
    
    try:
        binF = open(fileName, 'rb')
    except:
        logger.error("Can not open file {}".format(fileName))
        return 
    
    m253, = struct.unpack('b', binF.read(1))
    versionMajor, = struct.unpack('b', binF.read(1))
    versionMinor, = struct.unpack('b', binF.read(1))
    time, = struct.unpack('d', binF.read(8))
    timeStep, = struct.unpack('d', binF.read(8))

    for j in range(len(info)):
        countZBlock = info[j][5]
        countYBlock = info[j][4]
        countXBlock = info[j][3]
    
        coordZBlock = info[j][2] - offsetZ
        coordYBlock = info[j][1] - offsetY
        coordXBlock = info[j][0] - offsetX
    
        total = countZBlock * countYBlock * countXBlock * cellSize
    
        blockData = np.fromfile(binF, dtype=np.float64, count=total)
        blockData = blockData.reshape(countZBlock, countYBlock, countXBlock,
                                      cellSize);
        data[coordZBlock: coordZBlock + countZBlock,
             coordYBlock: coordYBlock + countYBlock,
             coordXBlock: coordXBlock + countXBlock, :] = blockData[:, :, :, :]
    binF.close()
    return data

  
def getDomainProperties(info):
    minZ = 0
    maxZ = 0
    
    minY = 0
    maxY = 0
    
    minX = 0
    maxX = 0
    
    for i in range(len(info)):
        if info[i][2] < minZ:
            minZ = info[i][2]
    
        if info[i][2] + info[i][5] > maxZ:
            maxZ = info[i][2] + info[i][5]
    
        if info[i][1] < minY:
            minY = info[i][1]
    
        if info[i][1] + info[i][4] > maxY:
            maxY = info[i][1] + info[i][4]
    
        if info[i][0] < minX:
            minX = info[i][2]
    
        if info[i][0] + info[i][3] > maxX:
            maxX = info[i][0] + info[i][3]
    
    countZ = maxZ - minZ
    countY = maxY - minY
    countX = maxX - minX
    
    offsetZ = -minZ
    offsetY = -minY
    offsetX = -minX
    
    return countZ, countY, countX, offsetZ, offsetY, offsetX
  
             
def getBinaryData(domFileName, lbinFileName):
    '''
      returns state from lbinFileName according to geometry from domFileName    
    '''
    info, cellSize, dx, dy, dz, dimension = readDomFile(domFileName)
    countZ, countY, countX, offsetZ, offsetY, offsetX = getDomainProperties(info)
    data = readBinFile(lbinFileName, info,
                       countZ, countY, countX,
                       offsetZ, offsetY, offsetX,
                       cellSize)
    return data
    
    
