# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin

Создаем массивы с геометрией области (номера функций в каждой точке каждого блока)
и сохраняем
После этого уже другой модуль по той же модели создает список функций (в т.ч. связки, которые появляются только тут после разрезания)
Нужен общий порядок нумерации функций.


'''
import os
import numpy as np
import subprocess
#from regions import BoundRegion
#from gridprocessing import *
#from datetime import date, datetime
#from temp_modifiers import *
#import time
#from block import Block
#from interconnect import Interconnect
#import copy
#from model import Model

from bound import bdict

devType = {"cpu":0, "gpu":1}

class BinaryModel(object):
    def __init__(self, dmodel):
        ':type dmodel: Model'
        print "Welcome to the binary model saver!"
        self.dmodel = dmodel

    def fill1dInitFuncs(self, funcArr, block, blockSize):
        pass

    def fill2dInitFuncs(self, funcArr, block, blockSize):
        print "Filling 2d initial function array."
        xc = blockSize[0]
        yc = blockSize[1]
        #1 fill default conditions
        funcArr[:] = 0#block.defaultInitial
        usedIndices = 0
        #2 fill user-defined conditions
        #2.1 collect user-defines initial conditions that are used in this block
        usedInitNums = [block.defaultInitial]
        for initReg in block.initialRegions:
            if not (initReg.initialNumber in usedInitNums):
                usedInitNums.append(initReg.initialNumber)
        #2.2 fill them    
        for initReg in block.initialRegions:    
            initFuncNum = usedIndices + usedInitNums.index(initReg.initialNumber)
            xstart, xend = initReg.getXrange(self.dmodel.gridStepX)
            ystart, yend = initReg.getYrange(self.dmodel.gridStepY)            
            funcArr[ystart:yend, xstart:xend] = initFuncNum             
                
        print "Used init nums:", usedInitNums
        
        #3 overwrite with values that come from Dirichlet bounds
        #3.1 collect dirichlet bound numbers that are used in this block
        usedIndices += len(usedInitNums)
        usedDirBoundNums = []
        for boundReg in block.boundRegions:
            if not (boundReg.boundNumber in usedDirBoundNums):
                if (self.dmodel.bounds[boundReg.boundNumber].btype == bdict["dirichlet"]):
                    usedDirBoundNums.append(boundReg.boundNumber) 
        
        usedDirBoundNums.sort()
        print "Used Dirichlet bound nums:", usedDirBoundNums
        
        
        
        #3.2 fill them
        for boundReg in block.boundRegions:
            if (self.dmodel.bounds[boundReg.boundNumber].btype == bdict["dirichlet"]):
                initFuncNum = usedIndices + usedDirBoundNums.index(boundReg.boundNumber)
                if boundReg.side == 0:       
                    idxX = 0         
                    ystart, yend = boundReg.getYrange(self.dmodel.gridStepY)                
                    funcArr[ystart:yend, idxX] = initFuncNum                
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = boundReg.getYrange(self.dmodel.gridStepY)                
                    funcArr[ystart:yend, idxX] = initFuncNum                    
                elif boundReg.side == 2:
                    idxY =  0
                    xstart, xend = boundReg.getXrange(self.dmodel.gridStepX)                
                    funcArr[idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = boundReg.getXrange(self.dmodel.gridStepX)
                    funcArr[idxY, xstart:xend] = initFuncNum
            

    def fill3dInitFuncs(self, funcArr, block, blockSize):
        pass


    def fill1dCompFuncs(self, funcArr, block, blockSize):
        pass

    def fill2dCompFuncs(self, funcArr, block, functionMap, blockSize):
        xc = blockSize[0]
        yc = blockSize[1]
        print "Filling 2d main function array."
        print "size:", xc, "x", yc
        haloSize = self.dmodel.getHaloSize()
        if haloSize>1:
            raise AttributeError("Halosize>1 is not supported yet")
        #1 default center is filled already
        funcArr[:] = 0
        funcArr[0,0]       = functionMap["e02"]
        funcArr[0,xc-1]    = functionMap["e12"]
        funcArr[yc-1,0]    = functionMap["e03"]
        funcArr[yc-1,xc-1] = functionMap["e13"]
        #side 0
        sideIdx = 0
        sideMap = functionMap["side"+str(sideIdx)]
        idxX = 0
        for idxY in range(1, yc-1):
            funcArr[idxY,idxX] = sideMap["default"]
        
        sideIdx = 1
        sideMap = functionMap["side"+str(sideIdx)]
        idxX = xc-1
        for idxY in range(1, yc-1):
            funcArr[idxY,idxX] = sideMap["default"]
        
        sideIdx = 2
        sideMap = functionMap["side"+str(sideIdx)]
        idxY = 0
        for idxX in range(1, xc-1):
            funcArr[idxY,idxX] = sideMap["default"]
        
        sideIdx = 3
        sideMap = functionMap["side"+str(sideIdx)]
        idxY = yc-1
        for idxX in range(1, xc-1):
            funcArr[idxY,idxX] = sideMap["default"]            
            
        #fill user-defined bounds
        for boundReg in block.boundRegions:
            sideMap = functionMap["side"+str(boundReg.side)]
            curf_idx = sideMap["userBound"+str(boundReg.boundNumber)]
            if boundReg.side == 0:                                            
                for idxX in range(0, haloSize):
                    ystart, yend = boundReg.getYrange(self.dmodel.gridStepY)
                    ystart = max(haloSize,ystart)
                    yend =  min(yc-haloSize,yend)
                    funcArr[ystart:yend, idxX] = curf_idx
            elif boundReg.side == 1:
                for idxX in range(xc - haloSize, xc):
                    ystart, yend = boundReg.getYrange(self.dmodel.gridStepY)
                    ystart = max(haloSize,ystart)
                    yend =  min(yc - haloSize,yend)
                    funcArr[ystart:yend, idxX] = curf_idx
            elif boundReg.side == 2:
                for idxY in range(0, haloSize):
                    xstart, xend = boundReg.getXrange(self.dmodel.gridStepX)
                    xstart = max(haloSize,xstart)
                    xend =  min(xc - haloSize,xend)
                    funcArr[idxY, xstart:xend] = curf_idx
            elif boundReg.side == 3:
                for idxY in range(yc - haloSize, yc):
                    xstart, xend = boundReg.getXrange(self.dmodel.gridStepX)
                    xstart = max(haloSize,xstart)
                    xend =  min(xc-haloSize,xend)
                    funcArr[idxY, xstart:xend] = curf_idx
        

    def fill3dCompFuncs(self, funcArr, block, blockSize):
        pass

    def fillBinarySettings(self):
        self.versionArr = np.zeros(3, dtype=np.uint8)
        self.versionArr[0] = 254
        self.versionArr[1] = 1
        self.versionArr[2] = 0

        self.timeAndStepArr = np.zeros(7, dtype=np.float64)
        self.timeAndStepArr[0] = self.dmodel.startTime
        self.timeAndStepArr[1] = self.dmodel.finishTime
        self.timeAndStepArr[2] = self.dmodel.timeStep
        self.timeAndStepArr[3] = self.dmodel.saveInterval
        self.timeAndStepArr[4] = self.dmodel.gridStepX
        self.timeAndStepArr[5] = self.dmodel.gridStepY
        self.timeAndStepArr[6] = self.dmodel.gridStepZ

        self.paramsArr = np.zeros(3, dtype=np.int32)
        self.paramsArr[0] = self.dmodel.getCellSize()
        self.paramsArr[1] = self.dmodel.getHaloSize()
        self.paramsArr[2] = self.dmodel.solverIndex
        
        self.toleranceArr = np.zeros(2, dtype=np.float64)
        self.toleranceArr[0] = self.dmodel.solverAtol
        self.toleranceArr[1] = self.dmodel.solverRtol
        
        print "Cell size:", self.paramsArr[0], "Halo size: ", self.paramsArr[1]

    def fillBinaryBlocks(self):
        print "Welcome to Blocks Data filler"
        print "following is the function mapping"
        print self.functionMaps
        
        self.blockCount = len(self.dmodel.blocks)
        self.blockCountArr = np.zeros(1, dtype=np.int32)
        self.blockCountArr[0] = self.blockCount
        self.blockPropArrList = []
        self.blockInitFuncArrList = []
        self.blockCompFuncArrList = []        
        for blockIdx in range(self.blockCount):
            print "Saving block", blockIdx
            block = self.dmodel.blocks[blockIdx]
            #1. Fill block params
            blockDim = block.dimension
            cellCountList = block.getCellCount(self.dmodel.gridStepX, self.dmodel.gridStepY,
                                           self.dmodel.gridStepZ )
            cellOffsetList = block.getCellOffset(self.dmodel.gridStepX, self.dmodel.gridStepY,
                                           self.dmodel.gridStepZ )
            cellCount = cellCountList[0]*cellCountList[1]*cellCountList[2]
            yc, xc = cellCountList[1] , cellCountList[0]

            blockPropArr = np.zeros(4+2*blockDim, dtype=np.int32)
            blockInitFuncArr = np.zeros(cellCount, dtype=np.int16)
            blockCompFuncArr = np.zeros(cellCount, dtype=np.int16)

            blockPropArr[0] = blockDim
            mapping = self.dmodel.mapping[blockIdx]
            blockPropArr[1] = mapping[0]
            blockPropArr[2] = devType[ mapping[1] ]
            blockPropArr[3] = mapping[2]
            idx = 4
            blockPropArr[idx] = cellOffsetList[0]
            idx += 1
            if blockDim>1:
                blockPropArr[idx] = cellOffsetList[1]
                idx+=1
            if blockDim>2:
                blockPropArr[idx] = cellOffsetList[2]
                idx+=1
            blockPropArr[idx] = cellCountList[0]
            idx += 1
            if blockDim>1:
                blockPropArr[idx] = cellCountList[1]
                idx+=1
            if blockDim>2:
                blockPropArr[idx] = cellCountList[2]
            self.blockPropArrList.append(blockPropArr)
            print blockPropArr
            #2. Fill block functions
            if blockDim==1:
                self.fill1dInitFuncs(blockInitFuncArr, block, cellCountList)
                self.fill1dCompFuncs(blockCompFuncArr, block, cellCountList)
            elif blockDim==2:
                self.fill2dInitFuncs(blockInitFuncArr.reshape([yc, xc]), block, cellCountList)
                print blockInitFuncArr.reshape([yc, xc])
                self.fill2dCompFuncs(blockCompFuncArr.reshape([yc, xc]), block, self.functionMaps[blockIdx], cellCountList)                
                print blockCompFuncArr.reshape([yc, xc])
            elif blockDim==3:
                self.fill1dFuncs(blockInitFuncArr, block, cellCountList)
                self.fill3dFuncs(blockCompFuncArr, block, cellCountList)

            self.blockInitFuncArrList.append(blockInitFuncArr)
            self.blockCompFuncArrList.append(blockCompFuncArr)


    def interconnect1dFill(self, icIdx):
        ic = self.dmodel.interconnects[icIdx]
        icDim = self.dmodel.blocks[ic.block1].dimension - 1

        block1 = self.dmodel.blocks[ic.block1]
        block2 = self.dmodel.blocks[ic.block1]
        [b1xc, b1yc, b1zc] = block1.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xc, b2yc, b2zc] = block2.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b1xoff, b1yoff, b1zoff] = block1.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xoff, b2yoff, b2zoff] = block2.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        if (ic.block1Side==0) or (ic.block1Side==1):
            #x=const connection
            if b1yoff < b2yoff:
                b1off = b2yoff - b1yoff
                b2off = 0
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1off = 0
                b2off = b2yoff - b1yoff
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
        else:
            #y=const connection
            if b1xoff < b2xoff:
                b1off = b2xoff - b1xoff
                b2off = 0
                icLen = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1off = 0
                b2off = b2xoff - b1xoff
                icLen = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff

        print "Saving interconnect", icIdx, "part 1"
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = icLen
        icPropArr1[2] = ic.block1
        icPropArr1[3] = ic.block2
        icPropArr1[4] = ic.block1Side
        icPropArr1[5] = ic.block2Side
        icPropArr1[6] = b1off
        icPropArr1[7] = b2off
        self.icList.append(icPropArr1)
        print icPropArr1

        print "Saving interconnect", icIdx, "part 2"
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = icLen
        icPropArr2[2] = ic.block2
        icPropArr2[3] = ic.block1
        icPropArr2[4] = ic.block2Side
        icPropArr2[5] = ic.block1Side
        icPropArr2[6] = b2off
        icPropArr2[7] = b1off
        self.icList.append(icPropArr2)
        print icPropArr2

    def fillBinaryInterconnects(self):
        self.icCount = len(self.dmodel.interconnects)
        self.icCountArr = np.zeros(1, dtype=np.int32)
        self.icCountArr[0] = self.icCount*2
        print "saving", self.icCountArr[0], "ics"
        self.icList = []
        for icIdx in range(self.icCount):
            ic = self.dmodel.interconnects[icIdx]
            icDim = self.dmodel.blocks[ic.block1].dimension - 1
            if icDim == 1:
                self.interconnect1dFill(icIdx)

    
    #this will only work if saveFuncs was called and self.functionMaps are filled
    def saveDomain(self, fileName):
        print "saving domain..."
        #computing
        self.fillBinarySettings()
        #this will only work if saveFuncs was called and self.functionMaps are filled
        self.fillBinaryBlocks()
        self.fillBinaryInterconnects()

        #saving
        domfile = open(fileName, "wb")
        #1. Save common settings
        self.versionArr.tofile(domfile)
        self.timeAndStepArr.tofile(domfile)
        self.paramsArr.tofile(domfile)
        self.toleranceArr.tofile(domfile)

        #2. Save blocks
        self.blockCountArr.tofile(domfile)
        for blockIdx in range(self.blockCount):
            self.blockPropArrList[blockIdx].tofile(domfile)
            self.blockInitFuncArrList[blockIdx].tofile(domfile)
            self.blockCompFuncArrList[blockIdx].tofile(domfile)

        #3. Save interconnects
        self.icCountArr.tofile(domfile)
        for icArr in self.icList:
            icArr.tofile(domfile)
        domfile.close()
    
    
    def saveFuncs(self, fileName):
        self.functionMaps = self.dmodel.createCPPandGetFunctionMaps(fileName)

    def compileFuncs(self, fileName):
        dirName = os.path.abspath(os.path.dirname(fileName))
        print "compiling..."
        #command = "nvcc "+ fileName + " -shared  -O3 -o libuserfuncs.so -Xcompiler -fPIC"
        command = "gcc "+ fileName + " -shared  -O3 -o " + dirName+"/libuserfuncs.so -fPIC"
        print command
        PIPE = subprocess.PIPE
        p = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
        print p.stdout.read()
        print "compilation finished"


    def createRunFile(self, OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName):
        print "generating launcher script..."
        flag = 0
        if finishTimeProvided: flag+=1
        else: finishTime = -1.1
        if continueEnabled: flag +=2
        else: continueFileName = "n_a"
        #print OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName
        
        runFile = open(OutputRunFile, "w")
        conn = self.dmodel.connection
        projFolder = conn.workspace+"/"+self.dmodel.projectName
        nodeCount = self.dmodel.getNodeCount()
        runFile.write("echo Welcome to generated kernel launcher!\n")
        runFile.write("export LD_LIBRARY_PATH="+projFolder+":$LD_LIBRARY_PATH\n")
        runFile.write("srun -N "+str(nodeCount)+ " -p debug "+conn.solverExecutable+" "+DomFileName+" "+str(flag)+" "+str(finishTime)+" "+continueFileName+ "\n")
        runFile.close()

