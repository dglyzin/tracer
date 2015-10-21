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
        print "Filling 1d initial function array."
        xc = blockSize[0]        
        #1 fill default conditions
        usedInitNums = [block.defaultInitial]
        initFuncNum = usedInitNums.index(block.defaultInitial)         
        funcArr[:] = initFuncNum
                
        #2 fill user-defined conditions
        #2.1 collect user-defines initial conditions that are used in this block        
        for initReg in block.initialRegions:
            if not (initReg.initialNumber in usedInitNums):
                usedInitNums.append(initReg.initialNumber)
        #2.2 fill them    
        for initReg in block.initialRegions:    
            initFuncNum = usedInitNums.index(initReg.initialNumber)
            xstart, xend = self.dmodel.getXrange(block, initReg.xfrom, initReg.xto)                        
            funcArr[xstart:xend] = initFuncNum             
                
        print "Used init nums:", usedInitNums
        
        #3 overwrite with values that come from Dirichlet bounds
        #3.1 collect dirichlet bound numbers that are used in this block
        usedIndices = len(usedInitNums)
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
                elif boundReg.side == 1:
                    idxX = xc - 1                               
                funcArr[idxX] = initFuncNum                    
                
        
        

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
            xstart, xend = self.dmodel.getXrange(block, initReg.xfrom, initReg.xto)
            ystart, yend = self.dmodel.getYrange(block, initReg.yfrom, initReg.yto)            
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
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto)    
                    funcArr[ystart:yend, idxX] = initFuncNum                
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto)           
                    funcArr[ystart:yend, idxX] = initFuncNum                    
                elif boundReg.side == 2:
                    idxY =  0
                    xstart, xend =self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto) 
                    funcArr[idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend = self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto)
                    funcArr[idxY, xstart:xend] = initFuncNum
            

    def fill3dInitFuncs(self, funcArr, block, blockSize):
        print "Filling 3d initial function array."
        xc = blockSize[0]
        yc = blockSize[1]
        zc = blockSize[2]
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
            xstart, xend = self.dmodel.getXrange(block, initReg.xfrom, initReg.xto)
            ystart, yend = self.dmodel.getYrange(block, initReg.yfrom, initReg.yto)            
            zstart, zend = self.dmodel.getYrange(block, initReg.zfrom, initReg.zto)
            funcArr[zstart:zend, ystart:yend, xstart:xend] = initFuncNum             
                
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
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto)    
                    zstart, zend = self.dmodel.getZrange(block, boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, ystart:yend, idxX] = initFuncNum                
                elif boundReg.side == 1:
                    idxX = xc - 1
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto)           
                    zstart, zend = self.dmodel.getZrange(block, boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, ystart:yend, idxX] = initFuncNum                    
                elif boundReg.side == 2:
                    idxY =  0
                    xstart, xend =self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto)
                    zstart, zend = self.dmodel.getZrange(block, boundReg.zfrom, boundReg.zto) 
                    funcArr[zstart:zend, idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 3:
                    idxY = yc-1
                    xstart, xend =self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto)
                    zstart, zend = self.dmodel.getZrange(block, boundReg.zfrom, boundReg.zto)
                    funcArr[zstart:zend, idxY, xstart:xend] = initFuncNum
                elif boundReg.side == 4:
                    idxZ =  0
                    xstart, xend =self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto)
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto) 
                    funcArr[idxZ, ystart:yend, xstart:xend] = initFuncNum
                elif boundReg.side == 5:
                    idxZ = zc-1
                    xstart, xend = self.dmodel.getXrange(block, boundReg.xfrom, boundReg.xto)
                    ystart, yend = self.dmodel.getYrange(block, boundReg.yfrom, boundReg.yto)
                    funcArr[idxZ, ystart:yend, xstart:xend] = initFuncNum


    def fill1dCompFuncs(self, funcArr, block, functionMap, blockSize):
        print "Filling 1d main function array."
        print "Function mapping for this block:"
        print functionMap
        xc = blockSize[0]        
        print "size:", xc
        haloSize = self.dmodel.getHaloSize()
        if haloSize>1:
            raise AttributeError("Halosize>1 is not supported yet")
        #1 fill center funcs
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]       
            
        #for [funcIdx, xfrom, xto] in functionMap["center"]:
        #    xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        for [funcIdx, xfromIdx, xtoIdx] in functionMap["center"]:            
            funcArr[xfromIdx:xtoIdx] = funcIdx
        #2 fill edges
        funcArr[0]       = functionMap["side0"]
        funcArr[xc-1]    = functionMap["side1"]
        
        
        

    def fill2dCompFuncs(self, funcArr, block, functionMap, blockSize):
        print "Filling 2d main function array."
        print "Function mapping for this block:"
        print functionMap
        xc = blockSize[0]
        yc = blockSize[1]        
        print "size:", xc, "x", yc
        haloSize = self.dmodel.getHaloSize()
        if haloSize>1:
            raise AttributeError("Halosize>1 is not supported yet")
        #1 fill center funcs
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]
        
            
        #for [funcIdx, xfrom, xto, yfrom, yto] in functionMap["center"]:
        #    xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        #    yfromIdx, ytoIdx = self.dmodel.getYrange(block, yfrom, yto)
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["center"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx
        #side 0
        #for [funcIdx, xfrom, xto, yfrom, yto] in functionMap["side0"]:            
        #    yfromIdx, ytoIdx = self.dmodel.getYrange(block, yfrom, yto)
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side0"]:            
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx
        #side 1
        #for [funcIdx, xfrom, xto, yfrom, yto] in functionMap["side1"]:            
        #    yfromIdx, ytoIdx = self.dmodel.getYrange(block, yfrom, yto)
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side1"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx
        #side 2
        #for [funcIdx, xfrom, xto, yfrom, yto] in functionMap["side2"]:
        #    xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side2"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx        
        #side 3
        #for [funcIdx, xfrom, xto, yfrom, yto] in functionMap["side3"]:
        #    xfromIdx, xtoIdx = self.dmodel.getXrange(block, xfrom, xto)
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx] in functionMap["side3"]:
            funcArr[yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx
        #2 fill edges
        funcArr[0,0]       = functionMap["v02"]
        funcArr[0,xc-1]    = functionMap["v12"]
        funcArr[yc-1,0]    = functionMap["v03"]
        funcArr[yc-1,xc-1] = functionMap["v13"]
        
        
        
    def fill3dCompFuncs(self, funcArr, block, functionMap, blockSize):
        print "Filling 2d main function array."
        print "Function mapping for this block:"
        print functionMap
        xc = blockSize[0]
        yc = blockSize[1]        
        zc = blockSize[2]
        print "size:", xc, "x", yc, "x", zc
        haloSize = self.dmodel.getHaloSize()
        if haloSize>1:
            raise AttributeError("Halosize>1 is not supported yet")
        #1 fill center funcs
        if "center_default" in functionMap:
            funcArr[:] = functionMap["center_default"]            
        #3d blocks
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx] in functionMap["center"]:
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx
            
        
        #2d sides    
        sides = functionMap["side0"] + functionMap["side1"] + functionMap["side2"] + \
                functionMap["side3"] + functionMap["side4"] + functionMap["side5"] 
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx] in sides:
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx        
        #1d edges
        edges = functionMap["edge02"] + functionMap["edge03"] + functionMap["edge12"] + functionMap["edge13"] + \
                functionMap["edge04"] + functionMap["edge05"] + functionMap["edge14"] + functionMap["edge15"] + \
                functionMap["edge24"] + functionMap["edge25"] + functionMap["edge34"] + functionMap["edge35"]     
        for [funcIdx, xfromIdx, xtoIdx, yfromIdx, ytoIdx, zfromIdx, ztoIdx] in edges:
            funcArr[zfromIdx:ztoIdx, yfromIdx:ytoIdx, xfromIdx:xtoIdx] = funcIdx        
        
        #point vertices
        funcArr[0,0,0]       = functionMap["v024"]
        funcArr[0,0,xc-1]    = functionMap["v124"]
        funcArr[0,yc-1,0]    = functionMap["v034"]
        funcArr[0,yc-1,xc-1] = functionMap["v134"]
        funcArr[zc-1,0,0]       = functionMap["v025"]
        funcArr[zc-1,0,xc-1]    = functionMap["v125"]
        funcArr[zc-1,yc-1,0]    = functionMap["v035"]
        funcArr[zc-1,yc-1,xc-1] = functionMap["v135"]
        
                

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
            zc, yc, xc = cellCountList[2], cellCountList[1] , cellCountList[0]

            blockPropArr = np.zeros(4+2*blockDim, dtype=np.int32)
            blockInitFuncArr = np.zeros(cellCount, dtype=np.int16)
            blockCompFuncArr = np.zeros(cellCount, dtype=np.int16)

            blockPropArr[0] = blockDim
            mapping = self.dmodel.mapping[blockIdx]
            blockPropArr[1] = mapping["NodeIdx"]
            blockPropArr[2] = devType[ mapping["DeviceType"] ]
            blockPropArr[3] = mapping["DeviceIdx"]
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
                print "Initial function indices:"
                print blockInitFuncArr
                self.fill1dCompFuncs(blockCompFuncArr, block, self.functionMaps[blockIdx], cellCountList)
                print "Computation function indices:"
                print blockCompFuncArr
            elif blockDim==2:
                self.fill2dInitFuncs(blockInitFuncArr.reshape([yc, xc]), block, cellCountList)
                print "Initial function indices:"
                print blockInitFuncArr.reshape([yc, xc])
                self.fill2dCompFuncs(blockCompFuncArr.reshape([yc, xc]), block, self.functionMaps[blockIdx], cellCountList)                
                print "Computation function indices:"
                print blockCompFuncArr.reshape([yc, xc])
            elif blockDim==3:
                self.fill3dInitFuncs(blockInitFuncArr.reshape([zc, yc, xc]), block, cellCountList)
                print "Initial function indices:"
                print blockInitFuncArr.reshape([zc, yc, xc])
                self.fill3dCompFuncs(blockCompFuncArr.reshape([zc, yc, xc]), block, self.functionMaps[blockIdx], cellCountList)                
                print "Computation function indices:"
                print blockCompFuncArr.reshape([zc, yc, xc])

            self.blockInitFuncArrList.append(blockInitFuncArr)
            self.blockCompFuncArrList.append(blockCompFuncArr)



    def interconnect0dFill(self, icIdx):
        ic = self.dmodel.interconnects[icIdx]
        icDim = 0
        print "Saving interconnect", icIdx, "part 1"
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = ic.block1
        icPropArr1[2] = ic.block2
        icPropArr1[3] = ic.block1Side
        icPropArr1[4] = ic.block2Side
        self.icList.append(icPropArr1)
        print icPropArr1

        print "Saving interconnect", icIdx, "part 2"
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = ic.block2
        icPropArr2[2] = ic.block1
        icPropArr2[3] = ic.block2Side
        icPropArr2[4] = ic.block1Side
        self.icList.append(icPropArr2)
        print icPropArr2




    def interconnect1dFill(self, icIdx):
        ic = self.dmodel.interconnects[icIdx]
        icDim = self.dmodel.blocks[ic.block1].dimension - 1

        block1 = self.dmodel.blocks[ic.block1]
        block2 = self.dmodel.blocks[ic.block2]
        [b1xc, b1yc, b1zc] = block1.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xc, b2yc, b2zc] = block2.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b1xoff, b1yoff, b1zoff] = block1.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xoff, b2yoff, b2zoff] = block2.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        
        print "Filling interconnect", icIdx, ": block1 off:", b1xoff, b1yoff, b1zoff, "; block2 off:", b2xoff, b2yoff, b2zoff 
        
        if (ic.block1Side==0) or (ic.block1Side==1):
            #x=const connection
            if b1yoff < b2yoff:
                b1off = b2yoff - b1yoff
                b2off = 0
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1off = 0
                b2off = b1yoff - b2yoff
                icLen = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
        else:
            #y=const connection
            if b1xoff < b2xoff:
                b1off = b2xoff - b1xoff
                b2off = 0
                icLen = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1off = 0
                b2off = b1xoff - b2xoff
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


    def interconnect2dFill(self, icIdx):
        ic = self.dmodel.interconnects[icIdx]
        icDim = self.dmodel.blocks[ic.block1].dimension - 1

        block1 = self.dmodel.blocks[ic.block1]
        block2 = self.dmodel.blocks[ic.block2]
        [b1xc, b1yc, b1zc] = block1.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xc, b2yc, b2zc] = block2.getCellCount(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b1xoff, b1yoff, b1zoff] = block1.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        [b2xoff, b2yoff, b2zoff] = block2.getCellOffset(self.dmodel.gridStepX,
                                    self.dmodel.gridStepY, self.dmodel.gridStepZ)
        
        print "Filling interconnect", icIdx, ": block1 off:", b1xoff, b1yoff, b1zoff, "; block2 off:", b2xoff, b2yoff, b2zoff 
        
        if (ic.block1Side==0) or (ic.block1Side==1):
            #x=const connection
            #Y=N
            if b1yoff < b2yoff:
                b1offN = b2yoff - b1yoff
                b2offN = 0
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offN = 0
                b2offN = b1yoff - b2yoff
                icLenN = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
            #Z=M
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        elif (ic.block1Side==2) or (ic.block1Side==3):
            #y=const connection
            #X=N
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            #Z=M
            if b1zoff < b2zoff:
                b1offM = b2zoff - b1zoff
                b2offM = 0
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b2zoff
            else:
                b1offM = 0
                b2offM = b1zoff - b2zoff
                icLenM = min(b1zoff+b1zc, b2zoff+b2zc) - b1zoff
        else:
            #z=const connection
            #X=N
            if b1xoff < b2xoff:
                b1offN = b2xoff - b1xoff
                b2offN = 0
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b2xoff
            else:
                b1offN = 0
                b2offN = b1xoff - b2xoff
                icLenN = min(b1xoff+b1xc, b2xoff+b2xc) - b1xoff
            #Y=M
            if b1yoff < b2yoff:
                b1offM = b2yoff - b1yoff
                b2offM = 0
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b2yoff
            else:
                b1offM = 0
                b2offM = b1yoff - b2yoff
                icLenM = min(b1yoff+b1yc, b2yoff+b2yc) - b1yoff
            

        print "Saving interconnect", icIdx, "part 1"
        icPropArr1 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr1[0] = icDim
        icPropArr1[1] = icLenM
        icPropArr1[2] = icLenN
        icPropArr1[3] = ic.block1
        icPropArr1[4] = ic.block2
        icPropArr1[5] = ic.block1Side
        icPropArr1[6] = ic.block2Side
        icPropArr1[7] = b1offM
        icPropArr1[8] = b1offN
        icPropArr1[9] = b2offM
        icPropArr1[10]= b2offN
        
        self.icList.append(icPropArr1)
        print icPropArr1

        print "Saving interconnect", icIdx, "part 2"
        icPropArr2 = np.zeros(5+3*icDim, dtype=np.int32)
        icPropArr2[0] = icDim
        icPropArr2[1] = icLenM
        icPropArr2[2] = icLenN
        icPropArr2[3] = ic.block2
        icPropArr2[4] = ic.block1
        icPropArr2[5] = ic.block2Side
        icPropArr2[6] = ic.block1Side
        icPropArr2[7] = b2offM
        icPropArr2[8] = b2offN
        icPropArr2[9] = b1offM
        icPropArr2[10]= b1offN
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
            if icDim == 0:
                self.interconnect0dFill(icIdx)
            elif icDim == 1:
                self.interconnect1dFill(icIdx)
            elif icDim == 2:
                self.interconnect2dFill(icIdx)

    
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
    
    
    def saveFuncs(self, fileName, tracerFolder):
        self.functionMaps = self.dmodel.createCPPandGetFunctionMaps(fileName, tracerFolder+"/hybriddomain")

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


    def createCOnlyRunFile(self, OutputRunFile, projectDir, tracerFolder, debug, 
                     DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName):
        '''
        in this case we run only c mpi workers and then process results
        '''    
        print "generating launcher script..."
        flag = 0
        if finishTimeProvided: flag+=1
        else: finishTime = -1.1
        if continueEnabled: flag +=2
        else: continueFileName = "n_a"
        #print OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName
        runFile = open(OutputRunFile, "w")        
        postprocessor = tracerFolder + "/hybriddomain/postprocessor.py"
         
        partitionOption = " "
        if debug:
            partitionOption = " -p debug "
        
        solverExecutable = tracerFolder+"/hybridsolver/bin/HS"
        
        nodeCount = self.dmodel.getNodeCount()
        runFile.write("echo Welcome to generated kernel launcher!\n")
        runFile.write("export LD_LIBRARY_PATH="+projectDir+":$LD_LIBRARY_PATH\n")
        runFile.write("srun -N "+str(nodeCount)+ partitionOption +solverExecutable+" "+DomFileName+" "+str(flag)+" "+str(finishTime)+" "+continueFileName+ "\n")
        runFile.write("srun -n1" + partitionOption +"python " + postprocessor +" " + projectDir+"/" )
        runFile.close()
   
                   
    def createMixRunFile(self, OutputSpmdFile, OutputRunFile, projectDir, tracerFolder, jobId, debug, 
                    DomFileName, finishTimeProvided, finish, continueEnabled, continueFileName):
        '''
          here we want to run mpi in mpmd mode with one python master process
          and some c workers
          1. create slurm-mpmd file
          2. create sh script
          no results handling needed, as it is done by python master          
        '''
        print "generating launcher script..."
        flag = 0
        if finishTimeProvided: flag+=1
        else: finishTime = -1.1
        if continueEnabled: flag +=2
        else: continueFileName = "n_a"
        #print OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName
                
        partitionOption = " "
        if debug:
            partitionOption = " -p debug "
        
        pythonMaster = tracerFolder+"/hybriddomain/mpimaster.py"
        solverExecutable = tracerFolder+"/hybridsolver/bin/HS"
        runOptions = DomFileName + " " + str(flag) + " " + str(finishTime) + " " + continueFileName
        
        nodeCount = self.dmodel.getNodeCount()
         
        spmdFile = open(OutputSpmdFile, "w")
        spmdFile.write("0 python " + pythonMaster + " " + str(jobId) + " " + runOptions + "\n")
        spmdFile.write("1-" + str(nodeCount) + " " + solverExecutable + " " + runOptions + "\n") 
        
        spmdFile.close()
        
        
        runFile = open(OutputRunFile, "w")
        runFile.write("echo Welcome to generated kernel launcher!\n")
        runFile.write("export LD_LIBRARY_PATH="+projectDir+":$LD_LIBRARY_PATH\n")
        #dirty trick to let python process consume one processor core 
        runFile.write("export OMP_NUM_THREADS=15\n")
        runFile.write("srun -N "+ str(nodeCount) + " "+ partitionOption+ "--multi-prog " + OutputSpmdFile +"\n")        
        #postprocessor = tracerFolder + "/hybriddomain/postprocessor.py"
        #runFile.write("srun -n1" + partitionOption +"python " + postprocessor +" " + projectDir+"/" )
        runFile.close()
        
