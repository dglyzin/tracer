# -*- coding: utf-8 -*-
'''
один входной аргумент - json файл, для которого уже выполнены расчеты
рядом с этим файлом будет создана папка с такимо же именем, в которую будут закачаны все 
вычисления, после чего будет для каждого файла нарисована картинка, а затем все 
склеено в видеофайл.
'''

import struct
import numpy as np
import matplotlib.pyplot as plt
import sys
import subprocess

from domainmodel.model import Model
import getpass
import paramiko, socket
from os import listdir

def readDomFile(projectDir):
    #reading dom file
    dom = open(projectDir+"/project.dom", 'rb')    
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
    
    return info



def getSortedBinaryFileList(projectDir):
    #get sorted binary file list
    unsortedBinFileList =  [ f for f in listdir(projectDir) if f.endswith(".bin") ]
    binTime = np.array([float(f.split('.bin')[0].split('project-')[1])  for f in unsortedBinFileList])    
    #print np.argsort(binTime)
    binFileList = [ unsortedBinFileList[idx] for idx in np.argsort(binTime)]
    print binFileList
    
    return binFileList
  
  
  
if __name__ == "__main__":
    if len(sys.argv)==1:
        print "Please specify a json file to read"
    else:
        jsonFile = sys.argv[1]
        #createMovie(jsonFile)
        getSortedBinaryFileList(jsonFile)