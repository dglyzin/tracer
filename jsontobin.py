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

from fileUtils import getSortedLoadBinFileList
import os


def createBinaries(inputFile, tracerFolder, jobId, finish, cont, debug, nortpng, outFileName, nocppgen):    
    finishTimeProvided = not (finish is None)   
    continueEnabled = not (cont is None)
    continueFnameProvided =  not (cont  == "/") if continueEnabled else False
    
    projectDir = os.path.dirname(inputFile)
    inProjectName, _ = os.path.splitext(inputFile)  
    if outFileName is None: 
        outProjectTitle = os.path.basename(inProjectName)
    else:
        outProjectTitle = outFileName 
    if inProjectName == '':
        print "Bad input file name"
        return

    OutputDataFile = os.path.join(projectDir, outProjectTitle) + ".dom"
    OutputFuncFile = os.path.join(projectDir, outProjectTitle) + ".cpp"
    OutputRunFile =  os.path.join(projectDir, outProjectTitle) + ".sh"
    OutputSpmdFile = os.path.join(projectDir, outProjectTitle) + ".spmd"

    #we want to find the last computed state to continue if user does not provide filename but tell us to continue
    print projectDir
    if continueEnabled:
        continueFileName = cont
    else: 
        continueFileName = "na"
    
    if continueEnabled and not continueFnameProvided:
        try:
            continueFileName = os.path.join(projectDir, getSortedLoadBinFileList(projectDir, outProjectTitle)[-1])
        except:
            print "No bin file to continue from!"
            return
  
    model = Model()
    model.loadFromFile(inputFile)
    
    print "\nMax derivative order is ", model.getMaxDerivOrder()
    
    #something not to be done here
    #model.delay_lst = model.determineDelay()
    #model.isdelay = bool(model.delay_lst)
    #print 'There is a delay?', model.isdelay
    #print 'Delays:', model.delay_lst, '\n'
   
    
    if model.isMapped:
        partModel = model
    else:
        partModel = partitionAndMap(model)
    
    bm = BinaryModel(partModel)
    delays = bm.saveFuncs(OutputFuncFile, tracerFolder,nocppgen)
    bm.saveDomain(OutputDataFile, delays)
    bm.compileFuncs(OutputFuncFile)
    
    print "jobID:", jobId

    if not (jobId is None):
        db, cur = dbc.getDbConn(args.jobId)
        dbc.setDbJobState(db, cur, jobId, JS_PREPROCESSING)
        dbc.freeDbConn(db, cur)
        bm.createMixRunFile(OutputSpmdFile, OutputRunFile, projectDir, outProjectTitle, tracerFolder, jobId, debug, 
                     OutputDataFile, finishTimeProvided, finish, continueEnabled, continueFileName)        
    else:               
        bm.createCOnlyRunFile(OutputRunFile, projectDir, outProjectTitle, tracerFolder, debug, nortpng,
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
    parser.add_argument('-outFileName', type = str, help="specify output project filename (fileName is default)")
    parser.add_argument('-nortpng', help="add this flag to avoid creating png in real time", action="store_true")
    parser.add_argument('-nocppgen', help="add this flag to avoid cpp generation", action="store_true")
    
    args = parser.parse_args()
  
    print "jsontobin input:", args
    createBinaries(args.fileName, args.tracerFolder, args.jobId, args.finish, args.cont, args.debug, args.nortpng, args.outFileName, args.nocppgen)
    
