# -*- coding: utf-8 -*-
'''
Модуль импортирует входной json
Создает по нему модель (включая и задачу, и мэппинг узлов-девайсов)
Создает бинарный файл с геометрией и свойствами области (*.dom)
Создает файл с функциями задачи (*.so)

Файл с состоянием не создается, т.к. у нас имеются функции, которые может вызвать ядро
для заполнения начальных значений


model -> mapped model -> domain.dom+funcs.cpp+run.sh
'''


from domainmodel.enums import *
import argparse
from domainmodel.model import Model
from domainmodel.binarymodel import BinaryModel
from domainmodel.decomposer import partitionAndMap

from fileUtils import getSortedBinFileList
import os
from domainmodel.dbConnector import setDbJobState


def createBinaries(inputFile, tracerFolder, jobId, finish, cont, debug):    
    finishTimeProvided = not (finish is None)   
    continueEnabled = not (cont is None)
    continueFnameProvided =  not (cont  == "/") if continueEnabled else False
    
    projectDir = os.path.dirname(inputFile)
    projectName, _ = os.path.splitext(inputFile)   
    projectTitle = os.path.basename(projectName)
    if projectName == '':
        print "Bad file name"
        return

    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    OutputRunFile = projectName+".sh"
    OutputSpmdFile = projectName+".spmd"

    #we want to find the last computed state to continue if user does not provide filename but tell us to continue
    print projectDir
    if continueEnabled:
        continueFileName = cont
    else: 
        continueFileName = "na"
    
    if continueEnabled and not continueFnameProvided:
        try:
            continueFileName = os.path.join(projectDir, getSortedBinFileList(projectDir, projectTitle)[-1])
        except:
            print "No bin file to continue from!"
            return
  
    model = Model()
    model.loadFromFile(inputFile)
    print "Max derivative order is ", model.getMaxDerivOrder()
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    bm.saveFuncs(OutputFuncFile, tracerFolder)
    bm.saveDomain(OutputDataFile)
    bm.compileFuncs(OutputFuncFile)
    
    print "jobID:", jobId

    if not (jobId is None):
        setDbJobState(jobId, JS_PREPROCESSING)
        bm.createMixRunFile(OutputSpmdFile, OutputRunFile, projectDir, tracerFolder, jobId, debug, 
                     OutputDataFile, finishTimeProvided, finish, continueEnabled, continueFileName)        
    else:               
        bm.createCOnlyRunFile(OutputRunFile, projectDir, tracerFolder, debug, 
                     OutputDataFile, finishTimeProvided, finish, continueEnabled, continueFileName)
                
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    parser.add_argument('tracerFolder', type = str, help = "Tracer Folder")
    
    #optional argument, unique job Id for identification in database 
    #if no id provided, db is not used and separate python mpi process is not included 
    parser.add_argument('-jobId', type = int, help = "unique job ID")
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    args = parser.parse_args()
  
    print "jsontobin input!", args.fileName, args.tracerFolder, args.jobId, args.finish, args.cont, args.debug 
    createBinaries(args.fileName, args.tracerFolder, args.jobId, args.finish, args.cont, args.debug)
    