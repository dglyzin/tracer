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

import domainmodel.criminal.tests_gen as ts
import shutil

devType = {"cpu":0, "gpu":1}
bdict = {"dirichlet":0, "neumann":1}


class BinaryModel(object):
    def __init__(self, dmodel):
        ':type dmodel: Model'
        print "Welcome to the binary model saver!"
        self.dmodel = dmodel

        
    #this will only work if saveFuncs was called and self.functionMaps are filled
    def saveDomain(self, fileName, delays):
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

        
        #1.1. delays 
        if len(delays) == 0:
            # without delays
            problemTypeArr = np.zeros(1, dtype=np.int32)
            problemTypeArr.tofile(domfile)
        else:
            # delays
            problemTypeArr = np.ones(1, dtype=np.int32)
            problemTypeArr.tofile(domfile)
            
            # delays length
            problemDelaysLen = np.array([len(delays)], dtype=np.int32)
            problemDelaysLen.tofile(domfile)
            
            # delays list
            problemDelaysList = np.array(delays, dtype=np.float64)
            problemDelaysList.tofile(domfile)
            #also we have to provide the number of states that can be stored in memory
            maxStatesCountArr = np.array([self.dmodel.getMaxStatesCount()], dtype=np.uint64)
            maxStatesCountArr.tofile(domfile)
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
        
        self.fillBinaryPlots()
        self.plotAndResCountArr.tofile(domfile)
        self.plotAndResPeriodsArr.tofile(domfile)
        print "plot periods:", self.plotAndResCountArr, self.plotAndResPeriodsArr          
        domfile.close()

    def saveFuncs(self, fileName, tracerFolder, nocppgen):
        '''
        Tests:
        In [12]: import domainmodel.binarymodel as bm
        In [12]: import tests.introduction.part_2_generators as p2
        In [12]: m=p2.get_model_for_tests("tests/2dTests/test2d_for_intervals_single.json")
        In [12]: mm=bm.BinaryModel(m)
        In [12]: mm.saveFuncs('test.cpp','/media/valdecar/forData/data/projectsNew/lab') 
        In [12]: mm.saveDomain('test.cpp',[])
        
        '''
        print("from saveFuncs")
        print(fileName)
        self.functionMaps, delays = self.dmodel.createCPPandGetFunctionMaps(fileName,
                                                                            tracerFolder+"/hybriddomain", nocppgen)
        '''
        if self.dmodel.dimension == 1:
            params = ts.test_templates_1d(self.dmodel)
            functionMaps = ts.test_domain_1d(self.dmodel)
            name = 'from_test_template_1d.cpp'
        elif self.dmodel.dimension == 2:
            params = ts.test_templates_2d(self.dmodel)
            functionMaps = ts.test_domain_2d(self.dmodel)
            name = 'from_test_template_2d.cpp'

        delays = params.delays
        self.functionMaps = functionMaps

        print("from saveFuncs")
        print(self.functionMaps)

        # copy and rename files
        pathToSave = os.path.join(tracerFolder, "hybriddomain")
        pathFrom = os.path.join(tracerFolder,
                                'hybriddomain',
                                'tests',
                                'introduction',
                                'src',
                                name)
        shutil.copy2(pathFrom, pathToSave)
        os.rename(os.path.join(pathToSave, name),
                  os.path.join(pathToSave, fileName))
        '''
        return(delays)

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


    def createCOnlyRunFile(self, OutputRunFile, projectDir, outProjectTitle, OutputDomFile, params):
        '''
        in this case we run only c mpi workers and then process results
        '''    
        print "generating launcher script..."
        flag = 0
        if not(params["finish"] is None): flag+=1
        else: finishTime = -1.1
        if not(params["cont"] is None): flag +=2
        else: params["cont"] = "n_a"
        if params["nortpng"]: flag+=4
        #print OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName
        runFile = open(OutputRunFile, "w")        
        postprocessor = params["tracerFolder"] + "/hybriddomain/postprocessor.py"
         

        solverExecutable = params["tracerFolder"]+"/hybridsolver/bin/HS"
        
        nodeCount = self.dmodel.getNodeCount()

        if params["partition"] is None:
            params["partition"] = " "
        else:
            params["partition"] = " -p " + params["partition"] + " "

        if params["nodes"] is None:
            params["nodes"] = self.dmodel.getNodeSpec()
        else:
            params["nodes"] = "-w "+params["nodes"]

        if params["mpimap"] is None:
            params["mpimap"] = ''
        elif  params["mpimap"] =='/':
            params["mpimap"] = '--map-by ppr:1:node:pe=16'
        else:
            params["mpimap"] = '--map-by '+ params["mpimap"]

        if params["affinity"] is None:
            params["affinity"] = '0-15'

        runFile.write("echo Welcome to generated kernel launcher!\n")
        runFile.write("export LD_LIBRARY_PATH="+projectDir+":$LD_LIBRARY_PATH\n")
        #runFile.write("export OMP_NUM_THREADS=16\n")
        runFile.write("export GOMP_CPU_AFFINITY='" + params["affinity"] + "'\n")
        runFile.write("salloc -N "+str(nodeCount) + " -n "+ str(nodeCount) + " " + params["nodes"] + params["partition"] + \
                      " mpirun "+ params["mpimap"] +" "+ solverExecutable+" "+OutputDomFile + \
                      " "+str(flag)+" "+str(finishTime) + " " + params["cont"] + "\n")
        #runFile.write("srun -N "+str(nodeCount)+" " +  partitionOption + " "+ solverExecutable+" "+DomFileName+" "+str(flag)+" "+str(finishTime)+" "+continueFileName+ "\n")
        runFile.write("srun -n1" + " " + params["nodes"] + params["partition"] +"python " + postprocessor +" " + projectDir+"/" +" " + outProjectTitle )
        runFile.close()
   
                   

    
    def generateState(self, fillFunc, dbinFileName, stateTime=0.0, stateTimeStep=1.0):
        ##!  uint8: 253
        ##!  uint8: file format version major
        ##!  uint8: file format version minor
        
        ##!  float64 current time 
        ##!  float64 current timestep
        ###  following is the N_B  blocks one by one
        ###  BEGINNING OF THE BLOCK##!   
        ##!  total*cellsize*float64: state 
        ###  END OF THE BLOCK
        dbinFile = open(dbinFileName, "wb")
        dbinVersionArr = np.zeros(3, dtype=np.uint8)
        dbinVersionArr[0] = 253
        dbinVersionArr[1] = 1
        dbinVersionArr[2] = 0

        dbinTimeAndStepArr = np.zeros(2, dtype=np.float64)
        dbinTimeAndStepArr[0] = stateTime
        dbinTimeAndStepArr[1] = stateTimeStep
        dbinVersionArr.tofile(dbinFile)
        dbinTimeAndStepArr.tofile(dbinFile)

        
        
        blockCount = len(self.dmodel.blocks)        
        domainDim = self.dmodel.dimension
        for blockIdx in range(blockCount):            
            block = self.dmodel.blocks[blockIdx]
            cellCountList = block.getCellCount(self.dmodel.gridStepX, self.dmodel.gridStepY,
                                           self.dmodel.gridStepZ )
            zc, yc, xc = cellCountList[2], cellCountList[1] , cellCountList[0]
            cellOffsetList = block.getCellOffset(self.dmodel.gridStepX, self.dmodel.gridStepY,
                                           self.dmodel.gridStepZ )
            cellCount = zc*yc*xc
            cellSize = self.dmodel.getCellSize()            

            blockState = np.zeros(cellCount*cellSize, dtype=np.float64)
            
            
        
            blockState.tofile(dbinFile)
